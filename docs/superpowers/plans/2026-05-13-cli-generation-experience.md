# CLI Generation Experience Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [x]`) syntax for tracking.

**Goal:** Add a first-class PyNest generation CLI that supports guided human prompts and one-shot agent commands with JSON output.

**Architecture:** Keep the existing `generate` commands as compatibility wrappers, but add primary root commands with direct Click wiring: `pynest new`, `pynest add ...`, and `pynest doctor`. Put generation behavior behind structured result objects and a presenter so file creation is testable separately from terminal output.

**Tech Stack:** Python 3.9+, Click, PyYAML, existing PyNest templates, pytest, Click `CliRunner`.

---

### Task 1: Structured Results And Presenter

**Files:**
- Create: `nest/cli/src/generate/generation_result.py`
- Create: `tests/test_cli/test_generation_result.py`

- [x] **Step 1: Write the failing tests**

Add tests that construct a generation result and assert both JSON and human rendering.

- [x] **Step 2: Run the tests to verify they fail**

Run: `uv run pytest tests/test_cli/test_generation_result.py -q`

Expected: FAIL because `nest.cli.src.generate.generation_result` does not exist.

- [x] **Step 3: Implement the result and presenter**

Create dataclasses for `GenerationError` and `GenerationResult`, plus `GenerationPresenter.render_json()` and `GenerationPresenter.render_human()`.

- [x] **Step 4: Run the tests to verify they pass**

Run: `uv run pytest tests/test_cli/test_generation_result.py -q`

Expected: PASS.

### Task 2: Application Generation Service

**Files:**
- Modify: `nest/cli/src/generate/generate_service.py`
- Test: `tests/test_cli/test_new_command.py`

- [x] **Step 1: Write failing tests for one-shot app creation**

Cover `pynest new sample --yes --json`, `.pynest.yaml`, `--dry-run`, and invalid database JSON errors.

- [x] **Step 2: Run tests to verify they fail**

Run: `uv run pytest tests/test_cli/test_new_command.py -q`

Expected: FAIL because `pynest new` does not exist.

- [x] **Step 3: Implement `GenerateService.generate_new_app()`**

Build a structured app generator that chooses the existing template, writes files through a tracked writer, writes `.pynest.yaml`, and returns `GenerationResult`.

- [x] **Step 4: Run tests to verify they pass**

Run: `uv run pytest tests/test_cli/test_new_command.py -q`

Expected: PASS.

### Task 3: New Root CLI Commands

**Files:**
- Create: `nest/cli/src/generate/generation_cli.py`
- Modify: `nest/cli/src/app_module.py`
- Test: `tests/test_cli/test_new_command.py`

- [x] **Step 1: Write failing tests for prompts and human output**

Cover `pynest new` with input, human summary output, and JSON-only output.

- [x] **Step 2: Run tests to verify they fail**

Run: `uv run pytest tests/test_cli/test_new_command.py -q`

Expected: FAIL because command wiring and prompts are missing.

- [x] **Step 3: Implement Click commands**

Attach `new`, `add`, and `doctor` to the root `nest_cli` group. Use Click prompts only when interactive or `--prompt` is passed. Ensure `--json` suppresses human output.

- [x] **Step 4: Run tests to verify they pass**

Run: `uv run pytest tests/test_cli/test_new_command.py -q`

Expected: PASS.

### Task 4: Add Commands And Metadata Discovery

**Files:**
- Modify: `nest/cli/src/generate/generate_service.py`
- Modify: `nest/cli/src/generate/generation_cli.py`
- Test: `tests/test_cli/test_add_command.py`

- [x] **Step 1: Write failing tests for `pynest add resource` and `pynest add gateway`**

Cover JSON output, created/updated files, `.pynest.yaml` metadata discovery, and dry-run.

- [x] **Step 2: Run tests to verify they fail**

Run: `uv run pytest tests/test_cli/test_add_command.py -q`

Expected: FAIL because `pynest add` behavior is missing.

- [x] **Step 3: Implement add commands**

Route to existing templates through tracked generation methods. Discover `.pynest.yaml` by walking up from the current directory, and fall back to defaults when metadata is absent.

- [x] **Step 4: Run tests to verify they pass**

Run: `uv run pytest tests/test_cli/test_add_command.py -q`

Expected: PASS.

### Task 5: Compatibility And Doctor

**Files:**
- Modify: `nest/cli/src/generate/generate_controller.py`
- Modify: `nest/cli/src/generate/generate_model.py`
- Modify: `nest/cli/src/generate/generate_service.py`
- Test: `tests/test_cli/test_generation_compatibility.py`

- [x] **Step 1: Write failing compatibility tests**

Cover old `pynest generate application -n app`, old `pynest generate resource -n users`, and `pynest doctor --json`.

- [x] **Step 2: Run tests to verify they fail**

Run: `uv run pytest tests/test_cli/test_generation_compatibility.py -q`

Expected: FAIL where compatibility output or doctor is missing.

- [x] **Step 3: Route old commands through new behavior**

Keep old options valid and render improved human output. Add optional `--json`, `--dry-run`, and `--force` where safe.

- [x] **Step 4: Run tests to verify they pass**

Run: `uv run pytest tests/test_cli/test_generation_compatibility.py -q`

Expected: PASS.

### Task 6: Docs And Verification

**Files:**
- Modify: `README.md`
- Modify: `docs/cli.md`

- [x] **Step 1: Update docs**

Document `pynest new`, prompt mode, one-shot agent mode, `pynest add`, `pynest doctor`, and compatibility commands.

- [x] **Step 2: Run focused tests**

Run: `uv run pytest tests/test_cli -q`

Expected: PASS.

- [x] **Step 3: Run full tests**

Run: `uv run pytest tests -q`

Expected: PASS.

- [x] **Step 4: Check worktree**

Run: `git status --short`

Expected: only intentional changed files.

## Self-Review

Spec coverage:

- Human prompt flow: Task 3.
- Agent one-shot JSON flow: Tasks 1-3.
- `new`, `add`, `doctor`: Tasks 3-5.
- Compatibility: Task 5.
- Visual terminal output: Task 1 and Task 3.
- Project metadata: Task 2 and Task 4.
- Tests and docs: Tasks 1-6.

Placeholder scan: no implementation placeholders remain in task outcomes; each task has concrete files and commands.

Scope note: this plan implements the first production slice from the spec. It does not add a heavy frontend or any future app preset beyond API/CLI because the spec intentionally deferred that.
