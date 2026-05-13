import json
from pathlib import Path

import yaml
from click.testing import CliRunner

from nest.cli.src.app_module import nest_cli


def test_new_command_creates_app_with_json_output():
    runner = CliRunner()

    with runner.isolated_filesystem():
        result = runner.invoke(
            nest_cli,
            ["new", "sample", "--database", "sqlite", "--async", "--yes", "--json"],
        )

        assert result.exit_code == 0, result.output
        payload = json.loads(result.output)
        metadata = yaml.safe_load(Path("sample/.pynest.yaml").read_text())
        readme = Path("sample/README.md").read_text()
        pyproject = Path("sample/pyproject.toml").read_text()

        assert payload["status"] == "created"
        assert payload["operation"] == "new"
        assert payload["target"] == "sample"
        assert payload["preset"] == "api"
        assert payload["database"] == "sqlite"
        assert payload["async"] is True
        assert payload["package_manager"] == "uv"
        assert "sample/main.py" in payload["files_created"]
        assert "sample/.pynest.yaml" in payload["files_created"]
        assert "sample/pyproject.toml" in payload["files_created"]
        assert "sample/requirements.txt" not in payload["files_created"]
        assert Path("sample/src/app_module.py").exists()
        assert "uv sync" in readme
        assert "pip install -r requirements.txt" not in readme
        assert '"pynest-api[http,sqlite-async]",' in pyproject
        assert "aiosqlite" not in pyproject
        assert metadata == {
            "version": 1,
            "preset": "api",
            "database": "sqlite",
            "async": True,
            "package_manager": "uv",
            "source_root": "src",
        }


def test_new_command_dry_run_outputs_plan_without_writing_files():
    runner = CliRunner()

    with runner.isolated_filesystem():
        result = runner.invoke(
            nest_cli,
            ["new", "sample", "--database", "sqlite", "--dry-run", "--json"],
        )

        assert result.exit_code == 0, result.output
        payload = json.loads(result.output)

        assert payload["status"] == "planned"
        assert "sample/main.py" in payload["files_created"]
        assert not Path("sample").exists()


def test_new_command_defaults_to_uv_package_manager():
    runner = CliRunner()

    with runner.isolated_filesystem():
        result = runner.invoke(
            nest_cli,
            ["new", "sample", "--yes", "--json"],
        )

        assert result.exit_code == 0, result.output
        payload = json.loads(result.output)

        assert payload["package_manager"] == "uv"
        assert "sample/pyproject.toml" in payload["files_created"]
        assert "sample/requirements.txt" not in payload["files_created"]
        assert "uv sync" in payload["next_steps"]
        assert Path("sample/pyproject.toml").exists()
        assert "uv sync" in Path("sample/README.md").read_text()
        assert '"pynest-api[http]",' in Path("sample/pyproject.toml").read_text()


def test_new_command_can_still_create_requirements_file_explicitly():
    runner = CliRunner()

    with runner.isolated_filesystem():
        result = runner.invoke(
            nest_cli,
            [
                "new",
                "sample",
                "--package-manager",
                "requirements",
                "--yes",
                "--json",
            ],
        )

        assert result.exit_code == 0, result.output
        payload = json.loads(result.output)

        assert payload["package_manager"] == "requirements"
        assert "sample/requirements.txt" in payload["files_created"]
        assert "sample/pyproject.toml" not in payload["files_created"]
        assert "pip install -r requirements.txt" in payload["next_steps"]
        assert "pip install -r requirements.txt" in Path("sample/README.md").read_text()
        assert "pynest-api[http]" in Path("sample/requirements.txt").read_text()


def test_new_command_generates_granular_extras_for_each_database_flavor():
    runner = CliRunner()

    cases = [
        (["--database", "sqlite"], "pynest-api[http,sqlite]"),
        (["--database", "sqlite", "--async"], "pynest-api[http,sqlite-async]"),
        (["--database", "postgresql"], "pynest-api[http,postgresql]"),
        (
            ["--database", "postgresql", "--async"],
            "pynest-api[http,postgresql-async]",
        ),
        (["--database", "mysql"], "pynest-api[http,mysql]"),
        (["--database", "mysql", "--async"], "pynest-api[http,mysql-async]"),
        (["--database", "mongodb"], "pynest-api[http,mongodb]"),
        (["--preset", "cli"], "pynest-api[cli]"),
    ]

    with runner.isolated_filesystem():
        for index, (args, dependency) in enumerate(cases):
            app_name = f"app_{index}"
            result = runner.invoke(
                nest_cli,
                ["new", app_name, *args, "--yes", "--json"],
            )

            assert result.exit_code == 0, result.output
            assert f'"{dependency}",' in Path(app_name, "pyproject.toml").read_text()


def test_new_command_invalid_database_json_error():
    runner = CliRunner()

    with runner.isolated_filesystem():
        result = runner.invoke(
            nest_cli,
            ["new", "sample", "--database", "postgres", "--yes", "--json"],
        )

        assert result.exit_code == 1
        payload = json.loads(result.output)

        assert payload == {
            "status": "error",
            "operation": "new",
            "target": "sample",
            "error": {
                "code": "invalid_database",
                "message": "Unknown database 'postgres'. Use one of: postgresql, mysql, sqlite, mongodb.",
                "field": "database",
            },
        }


def test_new_command_prompt_creates_app_with_human_output():
    runner = CliRunner()

    with runner.isolated_filesystem():
        result = runner.invoke(
            nest_cli,
            ["new", "--prompt"],
            input="prompt_app\n1\n1\n1\n",
        )

        assert result.exit_code == 0, result.output
        assert "Application name" in result.output
        assert "Package manager:" in result.output
        assert "Creating application  prompt_app" in result.output
        assert "CREATE  prompt_app/main.py" in result.output
        assert "CREATE  prompt_app/pyproject.toml" in result.output
        assert "Application ready" in result.output
        assert "Next steps" in result.output
        assert Path("prompt_app/.pynest.yaml").exists()


def test_new_command_prompt_can_choose_async_database():
    runner = CliRunner()

    with runner.isolated_filesystem():
        result = runner.invoke(
            nest_cli,
            ["new", "--prompt"],
            input="async_app\n1\n2\ny\n1\n",
        )

        assert result.exit_code == 0, result.output
        metadata = yaml.safe_load(Path("async_app/.pynest.yaml").read_text())

        assert "Use async database access?" in result.output
        assert metadata["database"] == "sqlite"
        assert metadata["async"] is True
        assert metadata["package_manager"] == "uv"


def test_new_command_prompt_can_choose_requirements_package_manager():
    runner = CliRunner()

    with runner.isolated_filesystem():
        result = runner.invoke(
            nest_cli,
            ["new", "--prompt"],
            input="requirements_app\n1\n1\n2\n",
        )

        assert result.exit_code == 0, result.output
        metadata = yaml.safe_load(Path("requirements_app/.pynest.yaml").read_text())

        assert "Choose package manager" in result.output
        assert metadata["package_manager"] == "requirements"
        assert Path("requirements_app/requirements.txt").exists()
        assert not Path("requirements_app/pyproject.toml").exists()
