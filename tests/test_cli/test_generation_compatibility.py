import json
import os
from pathlib import Path

from click.testing import CliRunner

from nest.cli.src.app_module import nest_cli


def test_generate_application_compatibility_supports_json():
    runner = CliRunner()

    with runner.isolated_filesystem():
        result = runner.invoke(
            nest_cli,
            ["generate", "application", "-n", "legacy", "--json"],
        )

        assert result.exit_code == 0, result.output
        payload = json.loads(result.output)

        assert payload["operation"] == "new"
        assert payload["target"] == "legacy"
        assert payload["package_manager"] == "uv"
        assert Path("legacy/.pynest.yaml").exists()
        assert Path("legacy/pyproject.toml").exists()
        assert not Path("legacy/requirements.txt").exists()


def test_generate_application_compatibility_can_request_requirements():
    runner = CliRunner()

    with runner.isolated_filesystem():
        result = runner.invoke(
            nest_cli,
            [
                "generate",
                "application",
                "-n",
                "legacy",
                "--package-manager",
                "requirements",
                "--json",
            ],
        )

        assert result.exit_code == 0, result.output
        payload = json.loads(result.output)

        assert payload["package_manager"] == "requirements"
        assert Path("legacy/requirements.txt").exists()
        assert not Path("legacy/pyproject.toml").exists()


def test_generate_resource_compatibility_supports_json():
    runner = CliRunner()

    with runner.isolated_filesystem():
        create_result = runner.invoke(nest_cli, ["new", "sample", "--yes", "--json"])
        assert create_result.exit_code == 0, create_result.output

        os.chdir("sample")
        result = runner.invoke(
            nest_cli,
            ["generate", "resource", "-n", "users", "--json"],
        )

        assert result.exit_code == 0, result.output
        payload = json.loads(result.output)

        assert payload["operation"] == "add_resource"
        assert "src/users/users_module.py" in payload["files_created"]
        assert Path("src/users/users_module.py").exists()


def test_doctor_json_reports_project_metadata():
    runner = CliRunner()

    with runner.isolated_filesystem():
        create_result = runner.invoke(
            nest_cli,
            ["new", "sample", "--database", "sqlite", "--yes", "--json"],
        )
        assert create_result.exit_code == 0, create_result.output

        os.chdir("sample")
        result = runner.invoke(nest_cli, ["doctor", "--json"])

        assert result.exit_code == 0, result.output
        payload = json.loads(result.output)

        assert payload["status"] == "created"
        assert payload["operation"] == "doctor"
        assert payload["target"] == "."
        assert payload["preset"] == "api"
        assert payload["database"] == "sqlite"
        assert payload["warnings"] == []
