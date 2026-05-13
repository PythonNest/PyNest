import json
import os
from pathlib import Path

from click.testing import CliRunner

from nest.cli.src.app_module import nest_cli


def test_add_resource_uses_project_metadata_and_json_output():
    runner = CliRunner()

    with runner.isolated_filesystem():
        create_result = runner.invoke(
            nest_cli,
            ["new", "sample", "--database", "sqlite", "--yes", "--json"],
        )
        assert create_result.exit_code == 0, create_result.output

        os.chdir("sample")
        result = runner.invoke(nest_cli, ["add", "resource", "users", "--json"])

        assert result.exit_code == 0, result.output
        payload = json.loads(result.output)

        assert payload["status"] == "created"
        assert payload["operation"] == "add_resource"
        assert payload["target"] == "users"
        assert payload["database"] == "sqlite"
        assert "src/users/users_controller.py" in payload["files_created"]
        assert "src/users/users_entity.py" in payload["files_created"]
        assert "src/app_module.py" in payload["files_updated"]
        assert Path("src/users/users_module.py").exists()
        assert "UsersModule" in Path("src/app_module.py").read_text()


def test_add_gateway_creates_gateway_package_and_registers_module():
    runner = CliRunner()

    with runner.isolated_filesystem():
        create_result = runner.invoke(nest_cli, ["new", "sample", "--yes", "--json"])
        assert create_result.exit_code == 0, create_result.output

        os.chdir("sample")
        result = runner.invoke(nest_cli, ["add", "gateway", "chat", "--json"])

        assert result.exit_code == 0, result.output
        payload = json.loads(result.output)

        assert payload["operation"] == "add_gateway"
        assert "src/chat/chat_gateway.py" in payload["files_created"]
        assert "src/chat/chat_module.py" in payload["files_created"]
        assert Path("src/chat/chat_gateway.py").exists()
        assert "ChatModule" in Path("src/app_module.py").read_text()


def test_add_resource_dry_run_does_not_write_files():
    runner = CliRunner()

    with runner.isolated_filesystem():
        create_result = runner.invoke(nest_cli, ["new", "sample", "--yes", "--json"])
        assert create_result.exit_code == 0, create_result.output

        os.chdir("sample")
        result = runner.invoke(
            nest_cli,
            ["add", "resource", "users", "--dry-run", "--json"],
        )

        assert result.exit_code == 0, result.output
        payload = json.loads(result.output)

        assert payload["status"] == "planned"
        assert "src/users/users_controller.py" in payload["files_created"]
        assert not Path("src/users").exists()
