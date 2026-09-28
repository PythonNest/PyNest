from pathlib import Path

import pytest
import yaml

from nest.cli.src.generate.generate_service import GenerateService


@pytest.mark.parametrize(
    "db_type,is_async,is_cli,expected",
    [
        (None, False, False, (None, False, False)),
        ("sqlite", True, False, ("sqlite", True, False)),
        (None, False, True, ("", False, True)),
    ],
)
def test_generated_project_keeps_cli_settings_locally(
    tmp_path, monkeypatch, db_type, is_async, is_cli, expected
):
    monkeypatch.chdir(tmp_path)
    service = GenerateService()
    package_settings = Path(__file__).parents[2] / "nest" / "settings.yaml"
    assert not package_settings.exists()

    service.generate_app("sample", db_type, is_async, is_cli)

    project = tmp_path / "sample"
    assert yaml.safe_load((project / "settings.yaml").read_text())["config"]
    assert not package_settings.exists()
    monkeypatch.chdir(project / "src")
    assert service.get_metadata() == expected


def test_project_metadata_isolated_between_projects(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    service = GenerateService()
    service.generate_app("web", None, False, False)
    service.generate_app("database", "sqlite", True, False)

    monkeypatch.chdir(tmp_path / "web")
    assert service.get_metadata() == (None, False, False)
    monkeypatch.chdir(tmp_path / "database" / "src")
    assert service.get_metadata() == ("sqlite", True, False)
