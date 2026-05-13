import json

from nest.cli.src.generate.generation_result import (
    GenerationError,
    GenerationPresenter,
    GenerationResult,
)


def test_generation_result_renders_deterministic_json():
    result = GenerationResult(
        status="created",
        operation="new",
        target="demo",
        preset="api",
        database="sqlite",
        is_async=True,
        package_manager="uv",
        files_created=["demo/main.py", "demo/.pynest.yaml"],
        files_updated=["demo/src/app_module.py"],
        next_steps=["cd demo", "python main.py"],
    )

    payload = json.loads(GenerationPresenter.render_json(result))

    assert payload == {
        "status": "created",
        "operation": "new",
        "target": "demo",
        "preset": "api",
        "database": "sqlite",
        "async": True,
        "package_manager": "uv",
        "files_created": ["demo/main.py", "demo/.pynest.yaml"],
        "files_updated": ["demo/src/app_module.py"],
        "files_skipped": [],
        "warnings": [],
        "next_steps": ["cd demo", "python main.py"],
    }


def test_generation_result_renders_human_summary():
    result = GenerationResult(
        status="created",
        operation="new",
        target="demo",
        preset="api",
        database="none",
        is_async=False,
        package_manager="uv",
        files_created=["demo/main.py"],
        next_steps=["cd demo", "python main.py"],
    )

    output = GenerationPresenter.render_human(result, version="9.9.9", use_color=False)

    assert "PyNest 9.9.9" in output
    assert "Plan" in output
    assert "Creating application  demo" in output
    assert "Preset                api" in output
    assert "Package manager       uv" in output
    assert "Files" in output
    assert "CREATE  demo/main.py" in output
    assert "Application ready" in output
    assert "  cd demo" in output


def test_generation_result_renders_ansi_styles_for_humans():
    result = GenerationResult(
        status="created",
        operation="new",
        target="demo",
        preset="api",
        database="none",
        package_manager="uv",
        files_created=["demo/main.py"],
    )

    output = GenerationPresenter.render_human(result, version="9.9.9", use_color=True)

    assert "\x1b[" in output
    assert "CREATE" in output


def test_generation_error_renders_json_and_human_message():
    result = GenerationResult(
        status="error",
        operation="new",
        target="demo",
        error=GenerationError(
            code="invalid_database",
            message="Unknown database 'postgres'. Use one of: postgresql, mysql, sqlite, mongodb.",
            field="database",
        ),
    )

    payload = json.loads(GenerationPresenter.render_json(result))
    human = GenerationPresenter.render_human(result, use_color=False)

    assert payload == {
        "status": "error",
        "operation": "new",
        "target": "demo",
        "error": {
            "code": "invalid_database",
            "message": "Unknown database 'postgres'. Use one of: postgresql, mysql, sqlite, mongodb.",
            "field": "database",
        },
    }
    assert "Could not create application" in human
    assert "Reason" in human
    assert "Unknown database 'postgres'." in human
