import json
from dataclasses import dataclass, field
from typing import Dict, List, Optional

import click


@dataclass
class GenerationError:
    code: str
    message: str
    field: Optional[str] = None

    def to_dict(self) -> Dict[str, str]:
        payload = {"code": self.code, "message": self.message}
        if self.field:
            payload["field"] = self.field
        return payload


@dataclass
class GenerationResult:
    status: str
    operation: str
    target: str
    preset: Optional[str] = None
    database: Optional[str] = None
    is_async: bool = False
    package_manager: Optional[str] = None
    files_created: List[str] = field(default_factory=list)
    files_updated: List[str] = field(default_factory=list)
    files_skipped: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    next_steps: List[str] = field(default_factory=list)
    error: Optional[GenerationError] = None

    def to_dict(self) -> Dict:
        payload = {
            "status": self.status,
            "operation": self.operation,
            "target": self.target,
        }
        if self.error:
            payload["error"] = self.error.to_dict()
            return payload

        payload.update(
            {
                "preset": self.preset,
                "database": self.database,
                "async": self.is_async,
                "package_manager": self.package_manager,
                "files_created": self.files_created,
                "files_updated": self.files_updated,
                "files_skipped": self.files_skipped,
                "warnings": self.warnings,
                "next_steps": self.next_steps,
            }
        )
        return payload


class GenerationPresenter:
    @staticmethod
    def render_json(result: GenerationResult) -> str:
        return json.dumps(result.to_dict(), sort_keys=False)

    @staticmethod
    def render_human(
        result: GenerationResult, version: str = None, use_color: bool = True
    ) -> str:
        if result.error:
            return GenerationPresenter._render_error(result, use_color=use_color)
        if result.operation == "new":
            return GenerationPresenter._render_new_result(result, version, use_color)
        if result.operation.startswith("add_"):
            return GenerationPresenter._render_add_result(result, version, use_color)
        if result.operation == "doctor":
            return GenerationPresenter._render_doctor_result(result, version, use_color)
        return GenerationPresenter._render_generic_result(result, version, use_color)

    @staticmethod
    def _style(text: str, fg: str, use_color: bool, bold: bool = False) -> str:
        if not use_color:
            return text
        return click.style(text, fg=fg, bold=bold)

    @staticmethod
    def _render_header(version: str = None, use_color: bool = True) -> List[str]:
        header = "PyNest"
        if version:
            header = f"{header} {version}"
        return [GenerationPresenter._style(header, "cyan", use_color, bold=True), ""]

    @staticmethod
    def _render_new_result(
        result: GenerationResult, version: str = None, use_color: bool = True
    ) -> str:
        lines = GenerationPresenter._render_header(version, use_color)
        verb = "Creating application"
        if result.status == "planned":
            verb = "Planning application"
        lines.extend(
            [
                GenerationPresenter._section("Plan", use_color),
                f"{verb}  {result.target}",
                f"{'Preset':<22}{result.preset}",
                f"{'Database':<22}{result.database}",
                f"{'Async':<22}{'yes' if result.is_async else 'no'}",
                f"{'Package manager':<22}{result.package_manager}",
                "",
            ]
        )
        lines.extend(GenerationPresenter._render_file_operations(result, use_color))
        lines.extend(
            GenerationPresenter._render_finish(result, "Application", use_color)
        )
        return "\n".join(lines).rstrip() + "\n"

    @staticmethod
    def _render_add_result(
        result: GenerationResult, version: str = None, use_color: bool = True
    ) -> str:
        lines = GenerationPresenter._render_header(version, use_color)
        component = result.operation.removeprefix("add_")
        verb = f"Adding {component}"
        if result.status == "planned":
            verb = f"Planning {component}"
        lines.extend(
            [
                GenerationPresenter._section("Plan", use_color),
                f"{verb}  {result.target}",
                "",
            ]
        )
        lines.extend(GenerationPresenter._render_file_operations(result, use_color))
        lines.extend(
            GenerationPresenter._render_finish(
                result, component.capitalize(), use_color
            )
        )
        return "\n".join(lines).rstrip() + "\n"

    @staticmethod
    def _render_doctor_result(
        result: GenerationResult, version: str = None, use_color: bool = True
    ) -> str:
        lines = GenerationPresenter._render_header(version, use_color)
        lines.append(GenerationPresenter._section("Project", use_color))
        lines.append(f"Checking project  {result.target}")
        lines.append("")
        for warning in result.warnings:
            lines.append(
                f"WARN    {GenerationPresenter._style(warning, 'yellow', use_color)}"
            )
        if not result.warnings:
            lines.append("Project ready")
        return "\n".join(lines).rstrip() + "\n"

    @staticmethod
    def _render_generic_result(
        result: GenerationResult, version: str = None, use_color: bool = True
    ) -> str:
        lines = GenerationPresenter._render_header(version, use_color)
        lines.extend(GenerationPresenter._render_file_operations(result, use_color))
        lines.extend(
            GenerationPresenter._render_finish(result, "Generation", use_color)
        )
        return "\n".join(lines).rstrip() + "\n"

    @staticmethod
    def _render_file_operations(
        result: GenerationResult, use_color: bool = True
    ) -> List[str]:
        lines = []
        if result.files_created or result.files_updated or result.files_skipped:
            lines.append(GenerationPresenter._section("Files", use_color))
        for path in result.files_created:
            lines.append(
                f"{GenerationPresenter._style('CREATE', 'green', use_color)}  {path}"
            )
        for path in result.files_updated:
            lines.append(
                f"{GenerationPresenter._style('UPDATE', 'yellow', use_color)}  {path}"
            )
        for path in result.files_skipped:
            lines.append(
                f"{GenerationPresenter._style('SKIP', 'blue', use_color)}    {path}"
            )
        if lines:
            lines.append("")
        for warning in result.warnings:
            lines.append(
                f"{GenerationPresenter._style('WARN', 'yellow', use_color)}    {warning}"
            )
        if result.warnings:
            lines.append("")
        return lines

    @staticmethod
    def _render_finish(
        result: GenerationResult, noun: str, use_color: bool = True
    ) -> List[str]:
        status_text = f"{noun} ready" if result.status == "created" else f"{noun} plan"
        status_line = GenerationPresenter._style(
            status_text, "green", use_color, bold=True
        )
        lines = [status_line]
        if result.next_steps:
            lines.extend(["", GenerationPresenter._section("Next steps", use_color)])
            lines.extend(f"  {step}" for step in result.next_steps)
        return lines

    @staticmethod
    def _render_error(result: GenerationResult, use_color: bool = True) -> str:
        action = "complete generation"
        if result.operation == "new":
            action = "create application"
        elif result.operation.startswith("add_"):
            action = f"add {result.operation.removeprefix('add_')}"
        lines = [
            GenerationPresenter._style(f"Could not {action}", "red", use_color),
            "",
            "Reason",
            f"  {result.error.message}",
        ]
        return "\n".join(lines).rstrip() + "\n"

    @staticmethod
    def _section(text: str, use_color: bool) -> str:
        if not use_color:
            return text
        return GenerationPresenter._style(text, "cyan", use_color, bold=True)
