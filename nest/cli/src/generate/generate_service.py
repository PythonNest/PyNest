from pathlib import Path
from typing import Dict, Tuple

import click
import yaml

from nest.cli.templates.templates_factory import TemplateFactory
from nest.core import Injectable
from nest.cli.src.generate.generation_result import GenerationError, GenerationResult


VALID_DATABASES = ("none", "postgresql", "mysql", "sqlite", "mongodb")
RELATIONAL_DATABASES = ("postgresql", "mysql", "sqlite")
VALID_PRESETS = ("api", "cli")
DATABASE_EXTRAS = {
    ("sqlite", False): "sqlite",
    ("sqlite", True): "sqlite-async",
    ("postgresql", False): "postgresql",
    ("postgresql", True): "postgresql-async",
    ("mysql", False): "mysql",
    ("mysql", True): "mysql-async",
    ("mongodb", False): "mongodb",
}


@Injectable
class GenerateService:
    def __init__(self):
        self.template_factory = TemplateFactory()

    @staticmethod
    def get_metadata():
        config = {"db_type": None, "is_async": False, "is_cli": False}
        setting_path = Path(__file__).parent.parent.parent.parent / "settings.yaml"
        if setting_path.exists():
            with open(setting_path, "r") as file:
                file = yaml.load(file, Loader=yaml.FullLoader)
                config = file["config"]
        db_type = config["db_type"]
        is_async = config["is_async"]
        is_cli = config["is_cli"] if "is_cli" in config else False
        return db_type, is_async, is_cli

    def get_template(self, module_name: str):
        db_type, is_async, is_cli = self.get_metadata()
        template = self.template_factory.get_template(
            module_name=module_name, db_type=db_type, is_async=is_async, is_cli=is_cli
        )
        return template

    def generate_resource(self, name: str, path: str = None):
        """
        Create a new nest resource

        :param name: The name of the module
        :param path: The path where the module will be created, Must be in a scope of the src folder.

        The files structure are:
        ├── ...
        ├── src
        │    ├── __init__.py
        │    ├── module_name
                ├── __init__.py
                ├── module_name_controller.py
                ├── module_name_service.py
                ├── module_name_model.py
                ├── module_name_entity.py (only for databases)
                ├── module_name_module.py

        """
        if path is None:
            path = Path.cwd()
        template = self.get_template(name)
        template.generate_module(name, path)

    def generate_controller(self, name: str, path: str = None):
        """
        Create a new nest controller

        :param name: The name of the controller

        The files structure are:
        ├── ...
        ├── src
        │    ├── __init__.py
        │    ├── module_name
                ├── __init__.py
                ├── module_name_controller.py
        """
        template = self.get_template(name)
        if path is None:
            path = Path.cwd()
        with open(f"{path}/{name}_controller.py", "w") as f:
            f.write(template.generate_empty_controller_file())

    def generate_service(self, name: str, path: str = None):
        """
        Create a new nest service

        :param name: The name of the service

        The files structure are:
        ├── ...
        ├── src
        │    ├── __init__.py
        │    ├── module_name
                ├── __init__.py
                ├── module_name_service.py
        """
        template = self.get_template(name)
        if path is None:
            path = Path.cwd()
        with open(f"{path}/{name}_service.py", "w") as f:
            f.write(template.generate_empty_service_file())

    def generate_gateway(self, name: str, path: str = None):
        """
        Create a new nest WebSocket gateway feature package under src/<name>/.

        :param name: The name of the gateway (and package folder)
        :param path: Project root or directory containing src/ (optional)
        """
        self.generate_add_component(
            "gateway", name, path=path, dry_run=False, force=False
        )

    def generate_module(self, name: str, path: str = None):
        """
        Create a new nest module

        :param name: The name of the module
        :param path: The path where the module will be created

        The files structure are:
        ├── ...
        ├── src
        │    ├── __init__.py
        │    ├── module_name
                ├── __init__.py
                ├── module_name_module.py
        """
        template = self.get_template(name)
        if path is None:
            src_path = template.find_target_folder(Path.cwd(), "src")
            if src_path is None:
                raise Exception("src folder not found")
            path = Path(src_path)
        else:
            path = Path(path)
        module_file = path / f"{name}_module.py"
        with open(module_file, "w") as f:
            f.write(template.generate_empty_module_file())
        click.echo(click.style(f"CREATE src/{name}_module.py", fg="green"))
        app_module_path = path / "app_module.py"
        if app_module_path.exists():
            template.append_module_to_app(
                path_to_app_py=str(app_module_path),
                module_import_path=f"src.{name}_module",
            )
            click.echo(
                click.style(
                    f"UPDATE src/app_module.py  (registered {template.class_name})",
                    fg="yellow",
                )
            )
        click.echo(
            click.style(
                f"\nHint: {template.class_name} is an empty skeleton. "
                f"Add controllers/providers manually, or use "
                f"'pynest generate resource -n {name}' for a full CRUD scaffold.",
                fg="cyan",
            )
        )

    def generate_app(self, app_name: str, db_type: str, is_async: bool, is_cli: bool):
        """
        Create a new nest app

        :param app_name: The name of the app
        :param db_type: The type of the database
        :param is_async: Whether the project should be async or not
        :param is_cli: Whether the project should be a CLI project or not

        The files structure are:
        ├── ...
        ├── src
        │    ├── __init__.py
        │    ├── app_name
                ├── __init__.py
                ├── app_name_controller.py
                ├── app_name_service.py
                ├── app_name_model.py
                ├── app_name_entity.py (only for databases)
                ├── app_name_module.py
        """
        template = self.template_factory.get_template(
            module_name=app_name, db_type=db_type, is_async=is_async, is_cli=is_cli
        )
        template.generate_project(app_name)

    def generate_new_app(
        self,
        app_name: str,
        preset: str = "api",
        database: str = "none",
        is_async: bool = False,
        path: str = None,
        package_manager: str = "uv",
        dry_run: bool = False,
        force: bool = False,
    ) -> GenerationResult:
        """
        Create a new PyNest application and return a structured generation result.
        """
        app_name = (app_name or "").strip()
        target = app_name or "."
        if not app_name:
            return self._generation_error(
                operation="new",
                target=target,
                code="missing_app_name",
                message="Application name is required.",
                field="app_name",
            )

        preset = (preset or "api").strip().lower()
        if preset not in VALID_PRESETS:
            return self._generation_error(
                operation="new",
                target=target,
                code="invalid_preset",
                message=f"Unknown preset '{preset}'. Use one of: api, cli.",
                field="preset",
            )

        database = (database or "none").strip().lower()
        if database not in VALID_DATABASES:
            return self._generation_error(
                operation="new",
                target=target,
                code="invalid_database",
                message=(
                    f"Unknown database '{database}'. Use one of: "
                    "postgresql, mysql, sqlite, mongodb."
                ),
                field="database",
            )

        if preset == "cli" and database != "none":
            return self._generation_error(
                operation="new",
                target=target,
                code="unsupported_database",
                message="CLI applications do not support database scaffolding.",
                field="database",
            )

        package_manager = (package_manager or "requirements").strip().lower()
        if package_manager not in ("requirements", "uv"):
            return self._generation_error(
                operation="new",
                target=target,
                code="invalid_package_manager",
                message=(
                    f"Unknown package manager '{package_manager}'. "
                    "Use one of: requirements, uv."
                ),
                field="package_manager",
            )

        if database not in RELATIONAL_DATABASES:
            is_async = False

        base_path = Path(path).expanduser() if path else Path.cwd()
        root_path = base_path / app_name
        if root_path.exists() and not force:
            return self._generation_error(
                operation="new",
                target=self._relative_path(root_path),
                code="target_exists",
                message=f"Target directory '{self._relative_path(root_path)}' already exists.",
                field="app_name",
            )

        db_type = None if database == "none" else database
        template = self.template_factory.get_template(
            module_name=app_name,
            db_type=db_type,
            is_async=is_async,
            is_cli=preset == "cli",
        )

        result = GenerationResult(
            status="planned" if dry_run else "created",
            operation="new",
            target=self._relative_path(root_path),
            preset=preset,
            database=database,
            is_async=is_async,
            package_manager=package_manager,
            next_steps=self._next_steps(app_name, preset, package_manager),
        )

        src_path = root_path / "src"
        if not dry_run:
            root_path.mkdir(parents=True, exist_ok=True)
            src_path.mkdir(parents=True, exist_ok=True)

        if preset == "cli":
            self._track_file(
                root_path / "main.py",
                self._cli_main_file(),
                result,
                dry_run=dry_run,
                force=force,
            )
        else:
            self._track_file(
                root_path / "main.py",
                template.main_file(),
                result,
                dry_run=dry_run,
                force=force,
            )

        self._track_file(
            root_path / "README.md",
            self._readme_file(app_name, preset, database, is_async, package_manager),
            result,
            dry_run=dry_run,
            force=force,
        )
        requirements_content = self._requirements_file(preset, database, is_async)
        if package_manager == "uv":
            self._track_file(
                root_path / "pyproject.toml",
                self._pyproject_file(app_name, requirements_content),
                result,
                dry_run=dry_run,
                force=force,
            )
        else:
            self._track_file(
                root_path / "requirements.txt",
                requirements_content,
                result,
                dry_run=dry_run,
                force=force,
            )
        self._track_file(
            root_path / ".pynest.yaml",
            self._metadata_file(preset, database, is_async, package_manager),
            result,
            dry_run=dry_run,
            force=force,
        )
        if database != "none":
            self._track_file(
                root_path / ".env.example",
                self._env_example_file(database),
                result,
                dry_run=dry_run,
                force=force,
            )
            gitignore_content = template.gitignore_file()
            if gitignore_content:
                self._track_file(
                    root_path / ".gitignore",
                    gitignore_content,
                    result,
                    dry_run=dry_run,
                    force=force,
                )

        self._track_file(
            src_path / "__init__.py",
            "",
            result,
            dry_run=dry_run,
            force=force,
        )
        self._track_file(
            src_path / "app_module.py",
            template.app_file(),
            result,
            dry_run=dry_run,
            force=force,
        )
        self._track_file(
            src_path / "app_controller.py",
            template.app_controller_file(),
            result,
            dry_run=dry_run,
            force=force,
        )
        self._track_file(
            src_path / "app_service.py",
            template.app_service_file(),
            result,
            dry_run=dry_run,
            force=force,
        )
        config_content = template.config_file()
        if config_content:
            self._track_file(
                src_path / "config.py",
                config_content,
                result,
                dry_run=dry_run,
                force=force,
            )

        return result

    def generate_add_component(
        self,
        component_type: str,
        name: str,
        path: str = None,
        dry_run: bool = False,
        force: bool = False,
    ) -> GenerationResult:
        """
        Add a resource or component to an existing PyNest application.
        """
        component_type = (component_type or "").strip().lower()
        name = (name or "").strip()
        operation = f"add_{component_type}"
        if not name:
            return self._generation_error(
                operation=operation,
                target=".",
                code="missing_name",
                message=f"{component_type.capitalize()} name is required.",
                field="name",
            )

        if component_type not in (
            "resource",
            "module",
            "controller",
            "service",
            "gateway",
        ):
            return self._generation_error(
                operation=operation,
                target=name,
                code="invalid_component",
                message=(
                    f"Unknown component '{component_type}'. Use one of: "
                    "resource, module, controller, service, gateway."
                ),
                field="component",
            )

        project_root, src_path, metadata = self._discover_project(path)
        if src_path is None or not src_path.exists():
            return self._generation_error(
                operation=operation,
                target=name,
                code="source_root_missing",
                message="src folder was not found. Run this inside a PyNest app, or pass --path.",
                field="path",
            )

        database = metadata.get("database") or "none"
        is_async = bool(metadata.get("async", False))
        preset = metadata.get("preset") or "api"
        db_type = None if database == "none" else database
        if database not in RELATIONAL_DATABASES:
            is_async = False

        template = self.template_factory.get_template(
            module_name=name,
            db_type=db_type,
            is_async=is_async,
            is_cli=preset == "cli",
        )
        result = GenerationResult(
            status="planned" if dry_run else "created",
            operation=operation,
            target=name,
            preset=preset,
            database=database,
            is_async=is_async,
            package_manager=metadata.get("package_manager") or "uv",
        )

        if component_type == "resource":
            self._plan_resource(name, src_path, template, result, dry_run, force)
        elif component_type == "module":
            self._plan_module(name, src_path, template, result, dry_run, force)
        elif component_type == "controller":
            self._track_file(
                src_path / f"{name}_controller.py",
                template.generate_empty_controller_file(),
                result,
                dry_run=dry_run,
                force=force,
            )
        elif component_type == "service":
            self._track_file(
                src_path / f"{name}_service.py",
                template.generate_empty_service_file(),
                result,
                dry_run=dry_run,
                force=force,
            )
        elif component_type == "gateway":
            self._plan_gateway(name, src_path, template, result, dry_run, force)

        return result

    def doctor_project(self, path: str = None) -> GenerationResult:
        project_root, src_path, metadata = self._discover_project(path)
        app_module_path = src_path / "app_module.py"
        warnings = []
        if not (project_root / ".pynest.yaml").exists():
            warnings.append(".pynest.yaml was not found; using inferred defaults.")
        if not src_path.exists():
            warnings.append(f"{self._relative_path(src_path)} was not found.")
        if not app_module_path.exists():
            warnings.append(f"{self._relative_path(app_module_path)} was not found.")

        database = metadata.get("database") or "none"
        is_async = bool(metadata.get("async", False))
        if database not in RELATIONAL_DATABASES:
            is_async = False

        return GenerationResult(
            status="created",
            operation="doctor",
            target=self._relative_path(project_root),
            preset=metadata.get("preset") or "api",
            database=database,
            is_async=is_async,
            package_manager=metadata.get("package_manager") or "uv",
            warnings=warnings,
        )

    @staticmethod
    def _generation_error(
        operation: str, target: str, code: str, message: str, field: str = None
    ) -> GenerationResult:
        return GenerationResult(
            status="error",
            operation=operation,
            target=target,
            error=GenerationError(code=code, message=message, field=field),
        )

    @staticmethod
    def _track_file(
        path: Path,
        content: str,
        result: GenerationResult,
        dry_run: bool = False,
        force: bool = False,
    ) -> None:
        relative_path = GenerateService._relative_path(path)
        exists = path.exists()
        if exists and not force and not dry_run:
            result.files_skipped.append(relative_path)
            result.warnings.append(
                f"{relative_path} already exists; use --force to overwrite."
            )
            return
        if exists:
            result.files_updated.append(relative_path)
        else:
            result.files_created.append(relative_path)
        if dry_run:
            return
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content)

    @staticmethod
    def _discover_project(path: str = None) -> Tuple[Path, Path, Dict]:
        start = Path(path).expanduser() if path else Path.cwd()
        start = start.resolve()
        if start.name == "src":
            default_root = start.parent
            default_src = start
        else:
            default_root = start
            default_src = start / "src"

        for candidate in (start, *start.parents):
            metadata_path = candidate / ".pynest.yaml"
            if metadata_path.exists():
                metadata = yaml.safe_load(metadata_path.read_text()) or {}
                source_root = metadata.get("source_root", "src")
                return candidate, candidate / source_root, metadata

        return (
            default_root,
            default_src,
            {
                "preset": "api",
                "database": "none",
                "async": False,
                "package_manager": "uv",
                "source_root": "src",
            },
        )

    def _plan_resource(
        self,
        name: str,
        src_path: Path,
        template,
        result: GenerationResult,
        dry_run: bool,
        force: bool,
    ) -> None:
        app_module_path = src_path / "app_module.py"
        if not app_module_path.exists():
            result.status = "error"
            result.error = GenerationError(
                code="app_module_missing",
                message="src/app_module.py was not found. Run this inside a PyNest app, or pass --path.",
                field="path",
            )
            return

        module_path = src_path / name
        self._track_file(
            module_path / "__init__.py", "", result, dry_run=dry_run, force=force
        )
        self._track_file(
            module_path / f"{name}_module.py",
            template.module_file(),
            result,
            dry_run=dry_run,
            force=force,
        )
        self._track_file(
            module_path / f"{name}_controller.py",
            template.controller_file(),
            result,
            dry_run=dry_run,
            force=force,
        )
        self._track_file(
            module_path / f"{name}_service.py",
            template.service_file(),
            result,
            dry_run=dry_run,
            force=force,
        )
        model_content = template.model_file()
        if model_content:
            self._track_file(
                module_path / f"{name}_model.py",
                model_content,
                result,
                dry_run=dry_run,
                force=force,
            )
        entity_content = template.entity_file()
        if entity_content:
            self._track_file(
                module_path / f"{name}_entity.py",
                entity_content,
                result,
                dry_run=dry_run,
                force=force,
            )
        self._track_app_module_update(app_module_path, template, result, dry_run)

    def _plan_gateway(
        self,
        name: str,
        src_path: Path,
        template,
        result: GenerationResult,
        dry_run: bool,
        force: bool,
    ) -> None:
        app_module_path = src_path / "app_module.py"
        if not app_module_path.exists():
            result.status = "error"
            result.error = GenerationError(
                code="app_module_missing",
                message="src/app_module.py was not found. Run this inside a PyNest app, or pass --path.",
                field="path",
            )
            return

        module_path = src_path / name
        self._track_file(
            module_path / "__init__.py", "", result, dry_run=dry_run, force=force
        )
        self._track_file(
            module_path / f"{name}_gateway.py",
            template.generate_empty_gateway_file(),
            result,
            dry_run=dry_run,
            force=force,
        )
        self._track_file(
            module_path / f"{name}_module.py",
            template.generate_gateway_module_file(),
            result,
            dry_run=dry_run,
            force=force,
        )
        self._track_app_module_update(
            app_module_path,
            template,
            result,
            dry_run,
            module_import_path=f"src.{name}.{name}_module",
        )

    def _plan_module(
        self,
        name: str,
        src_path: Path,
        template,
        result: GenerationResult,
        dry_run: bool,
        force: bool,
    ) -> None:
        app_module_path = src_path / "app_module.py"
        self._track_file(
            src_path / f"{name}_module.py",
            template.generate_empty_module_file(),
            result,
            dry_run=dry_run,
            force=force,
        )
        if app_module_path.exists():
            self._track_app_module_update(
                app_module_path,
                template,
                result,
                dry_run,
                module_import_path=f"src.{name}_module",
            )

    def _track_app_module_update(
        self,
        app_module_path: Path,
        template,
        result: GenerationResult,
        dry_run: bool,
        module_import_path: str = None,
    ) -> None:
        relative_path = self._relative_path(app_module_path)
        if relative_path not in result.files_updated:
            result.files_updated.append(relative_path)
        if dry_run:
            return
        template.append_module_to_app(
            path_to_app_py=str(app_module_path),
            module_import_path=module_import_path,
        )

    @staticmethod
    def _relative_path(path: Path) -> str:
        try:
            return str(path.resolve().relative_to(Path.cwd().resolve()))
        except ValueError:
            return str(path)

    @staticmethod
    def _metadata_file(
        preset: str, database: str, is_async: bool, package_manager: str
    ) -> str:
        return yaml.safe_dump(
            {
                "version": 1,
                "preset": preset,
                "database": database,
                "async": is_async,
                "package_manager": package_manager,
                "source_root": "src",
            },
            sort_keys=False,
        )

    @staticmethod
    def _env_example_file(database: str) -> str:
        if database == "sqlite":
            return "SQLITE_DB_NAME=default_nest_db\n"
        if database == "mongodb":
            return (
                "DB_NAME=default_nest_db\n"
                "DB_HOST=localhost\n"
                "DB_USER=root\n"
                "DB_PASSWORD=root\n"
                "DB_PORT=27017\n"
            )
        prefix = "POSTGRESQL" if database == "postgresql" else database.upper()
        port = "5432" if database == "postgresql" else "3306"
        return (
            f"{prefix}_HOST=localhost\n"
            f"{prefix}_DB_NAME=default_nest_db\n"
            f"{prefix}_USER={database}\n"
            f"{prefix}_PASSWORD={database}\n"
            f"{prefix}_PORT={port}\n"
        )

    @staticmethod
    def _readme_file(
        app_name: str,
        preset: str,
        database: str,
        is_async: bool,
        package_manager: str,
    ) -> str:
        if preset == "cli":
            run_command = "python main.py app info"
        else:
            run_command = "python main.py"
        install_command = (
            "uv sync" if package_manager == "uv" else "pip install -r requirements.txt"
        )
        return f"""# {app_name}

Generated with PyNest.

## Setup

```bash
{install_command}
```

## Run

```bash
{run_command}
```

## Project

- Preset: {preset}
- Database: {database}
- Async: {"yes" if is_async else "no"}
- Package manager: {package_manager}

## Add code

```bash
pynest add resource users
pynest add gateway chat
```
"""

    @staticmethod
    def _requirements_file(preset: str, database: str, is_async: bool) -> str:
        return f"{GenerateService._pynest_dependency(preset, database, is_async)}\n"

    @staticmethod
    def _pynest_dependency(preset: str, database: str, is_async: bool) -> str:
        extras = []
        if preset == "cli":
            extras.append("cli")
        else:
            extras.append("http")

        database_extra = DATABASE_EXTRAS.get((database, is_async))
        if database_extra:
            extras.append(database_extra)

        if not extras:
            return "pynest-api"
        return f"pynest-api[{','.join(extras)}]"

    @staticmethod
    def _pyproject_file(app_name: str, requirements_content: str) -> str:
        dependencies = [
            line.strip()
            for line in requirements_content.splitlines()
            if line.strip() and not line.strip().startswith("#")
        ]
        dependency_lines = "\n".join(
            f'    "{dependency}",' for dependency in dependencies
        )
        package_name = app_name.replace("_", "-")
        return f"""[project]
name = "{package_name}"
version = "0.1.0"
requires-python = ">=3.9"
dependencies = [
{dependency_lines}
]
"""

    @staticmethod
    def _cli_main_file() -> str:
        return """from src.app_module import cli_app


if __name__ == "__main__":
    cli_app()
"""

    @staticmethod
    def _next_steps(app_name: str, preset: str, package_manager: str) -> list:
        install = (
            "uv sync" if package_manager == "uv" else "pip install -r requirements.txt"
        )
        run = "python main.py app info" if preset == "cli" else "python main.py"
        return [f"cd {app_name}", install, run]
