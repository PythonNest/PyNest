# PyNest CLI Generation Experience Design

## Purpose

PyNest should provide a generation CLI that feels excellent for humans and is reliable for agents. Humans should be able to start with a guided prompt and understand exactly what happened. Agents should be able to express the whole desired operation in one command and receive deterministic, machine-readable output.

This design improves the full generation surface:

- Creating applications.
- Adding resources, modules, controllers, services, and gateways.
- Terminal output, progress, summaries, errors, and generated starter project presentation.
- Compatibility with existing `pynest generate ...` commands.

## Current State

The current CLI exposes:

```bash
pynest generate application -n my_app
pynest generate resource -n users
pynest generate module -n auth
pynest generate controller -n users
pynest generate service -n users
pynest generate gateway -n chat
```

Observed gaps:

- The application command is functional but not memorable.
- Help text is sparse and does not explain common paths.
- Generation output is mostly file-level `CREATE` lines with little context.
- There is no guided flow for humans.
- There is no JSON output for agents.
- There is no dry-run plan.
- Validation errors are not consistently actionable.
- Generated app metadata is stored at package level as `nest/settings.yaml`; it should live inside the generated project.
- Docs and examples are partially out of date with generated structure.

## Recommended Approach

Add a new primary CLI surface and keep the current one as a compatibility layer.

New primary commands:

```bash
pynest new [APP_NAME]
pynest add resource NAME
pynest add module NAME
pynest add controller NAME
pynest add service NAME
pynest add gateway NAME
pynest doctor
```

Compatibility commands continue to work:

```bash
pynest generate application -n my_app
pynest generate resource -n users
```

The implementation should reuse the existing template classes where practical, but generation should route through a clearer application-generation service that can return a structured result instead of only printing during file writes.

## Human Experience

The human-first path is interactive:

```bash
pynest new
```

If the user omits required information and the terminal is interactive, PyNest prompts for it:

```text
PyNest 0.6.0

Create a new PyNest application

Application name: my-app
Preset:
  1. HTTP API
  2. CLI application
Choose preset [1]: 1
Database:
  1. None
  2. SQLite
  3. PostgreSQL
  4. MySQL
  5. MongoDB
Choose database [1]: 2
Use async database access? [y/N]: y

Creating application  my-app
Preset                HTTP API
Database              sqlite
Async                 yes

CREATE  my-app/main.py
CREATE  my-app/src/app_module.py
CREATE  my-app/src/app_controller.py
CREATE  my-app/src/app_service.py
CREATE  my-app/src/config.py
CREATE  my-app/README.md
CREATE  my-app/requirements.txt
CREATE  my-app/.pynest.yaml

Application ready

Next steps
  cd my-app
  pip install -r requirements.txt
  python main.py
```

The prompt should be helpful but not noisy:

- Ask only for missing information.
- Use defaults for the common path.
- Avoid prompting when `--yes` or `--json` is used.
- Do not prompt in non-interactive environments unless explicitly requested with `--prompt`.
- Show the final plan before writing if the operation is risky or overwrites are possible.

The human command should also support explicit flags:

```bash
pynest new my-app --preset api --database sqlite --async
```

## Agent Experience

The agent-first path is a complete, explicit command:

```bash
pynest new my-app --preset api --database sqlite --async --yes --json
```

Agents should not need a prompt. They should be able to specify the whole statement in one command.

Rules for agent-friendly behavior:

- `--json` implies non-interactive mode.
- `--yes` confirms default-safe choices and suppresses confirmation prompts.
- Missing required values in non-interactive mode should fail with a structured error.
- Output must be deterministic and parseable.
- File paths in JSON should be relative to the current working directory unless an absolute path was explicitly passed.
- Exit codes must distinguish success from validation errors and write failures.

Example JSON success output:

```json
{
  "status": "created",
  "operation": "new",
  "project": "my-app",
  "preset": "api",
  "database": "sqlite",
  "async": true,
  "files_created": [
    "my-app/main.py",
    "my-app/src/app_module.py",
    "my-app/src/app_controller.py",
    "my-app/src/app_service.py",
    "my-app/src/config.py",
    "my-app/README.md",
    "my-app/requirements.txt",
    "my-app/.pynest.yaml"
  ],
  "files_updated": [],
  "next_steps": [
    "cd my-app",
    "pip install -r requirements.txt",
    "python main.py"
  ]
}
```

Example JSON validation error:

```json
{
  "status": "error",
  "error": {
    "code": "invalid_database",
    "message": "Unknown database 'postgres'. Use one of: postgresql, mysql, sqlite, mongodb.",
    "field": "database"
  }
}
```

## Command Contract

### `pynest new`

Creates a new PyNest app.

Recommended options:

- `APP_NAME`: optional in interactive mode, required in non-interactive mode.
- `--preset api|cli`: generated app type. Default: `api`.
- `--database none|sqlite|postgresql|mysql|mongodb`: database integration. Default: `none`.
- `--async`: async database access for relational databases.
- `--path PATH`: parent directory for the new app. Default: current directory.
- `--package-manager requirements|uv`: generated dependency files. Default: `requirements`.
- `--prompt`: force interactive prompts.
- `--yes`: accept defaults and proceed without confirmation.
- `--dry-run`: show the generation plan without writing files.
- `--json`: output structured JSON and suppress human formatting.
- `--quiet`: only print essential information.
- `--force`: allow overwriting where explicitly supported.

### `pynest add`

Adds code to an existing PyNest app.

Recommended commands:

```bash
pynest add resource users
pynest add module auth
pynest add controller users
pynest add service users
pynest add gateway chat
```

Recommended shared options:

- `--path PATH`: target app or source directory.
- `--flat`: generate directly into the target path where applicable.
- `--dry-run`
- `--json`
- `--quiet`
- `--force`

`pynest add` should discover `.pynest.yaml` by walking up from the current directory. If metadata is missing, it should fall back to sensible defaults and explain how to fix the project.

### `pynest doctor`

Checks whether the current directory is a valid PyNest project.

It should report:

- Whether `.pynest.yaml` exists.
- App preset.
- Database settings.
- Whether `src/app_module.py` exists.
- Whether generation can safely add modules.

`doctor --json` should return the same information as structured data.

## Visual Terminal Design

Human output should be scannable and calm:

- Header with PyNest version and operation.
- Aligned key/value plan summary.
- Colored file operations: `CREATE`, `UPDATE`, `SKIP`, `ERROR`.
- Clear final status.
- Exact next steps.
- No decorative banners or excessive symbols.

Example:

```text
PyNest 0.6.0

Adding resource  users
Target           src/users
Database         sqlite

CREATE  src/users/__init__.py
CREATE  src/users/users_module.py
CREATE  src/users/users_controller.py
CREATE  src/users/users_service.py
CREATE  src/users/users_model.py
CREATE  src/users/users_entity.py
UPDATE  src/app_module.py  registered UsersModule

Resource ready
```

Error output should be specific and actionable:

```text
Could not add resource

Reason
  src/app_module.py was not found.

Fix
  Run this command inside a PyNest app, or pass --path to the app root.
```

When `--json` is used, no colored or human prose output should be emitted.

## Generated Project Presentation

Generated apps should look clean when opened by a human or an agent:

- Create `.pynest.yaml` in the generated project root.
- Generate a focused `README.md` with exact install, run, and add-resource commands.
- Generate `.env.example` for database presets.
- Keep starter API code minimal and formatted.
- Keep generated CLI app code minimal and runnable.
- Avoid adding a frontend or heavy visual app unless a future explicit preset asks for it.

Example `.pynest.yaml`:

```yaml
version: 1
preset: api
database: sqlite
async: true
source_root: src
```

## Architecture

Add a small generation result model:

- Operation name.
- Project or target path.
- Preset/database/async settings.
- Files created.
- Files updated.
- Files skipped.
- Warnings.
- Next steps.

Template writing should return this result instead of printing directly. A presentation layer should then render either:

- Human terminal output.
- JSON output.

This keeps generation behavior testable and avoids coupling file creation to terminal text.

Suggested internal split:

- `GenerateService`: command-facing orchestration.
- `ApplicationGenerator`: validates and creates new apps.
- `ComponentGenerator`: validates and adds resources/components.
- `GenerationResult`: structured result object.
- `GenerationPresenter`: human and JSON renderers.
- Existing templates: reused and gradually cleaned up.

## Compatibility

Existing commands should remain valid:

```bash
pynest generate application -n my_app
pynest generate resource -n users
```

They can internally call the new services and render the same improved output.

Compatibility mappings:

- `generate application -n NAME` -> `new NAME`.
- `generate resource -n NAME` -> `add resource NAME`.
- `generate module -n NAME` -> `add module NAME`.
- `generate controller -n NAME` -> `add controller NAME`.
- `generate service -n NAME` -> `add service NAME`.
- `generate gateway -n NAME` -> `add gateway NAME`.

## Testing

Tests should cover:

- `pynest new my-app --yes` creates the expected file tree.
- `pynest new my-app --database sqlite --async --yes` creates config and metadata.
- `pynest new --prompt` can be driven with Click's test input.
- `pynest new my-app --json --yes` emits valid JSON only.
- `pynest new my-app --dry-run` writes no files.
- Invalid database values produce actionable human errors and structured JSON errors.
- `pynest add resource users --json` reports created and updated files.
- Compatibility commands still work.
- Existing gateway generation tests continue to pass.

## Rollout

Implement in focused phases:

1. Add structured generation result and presenter.
2. Add `pynest new` with interactive, non-interactive, JSON, and dry-run modes.
3. Move app metadata to `.pynest.yaml`.
4. Add `pynest add` commands and route old `generate` commands through the new behavior.
5. Add `pynest doctor`.
6. Update docs and README examples.

The first implementation should prioritize `new`, `add resource`, JSON, dry-run, and compatibility. `doctor` can follow once metadata discovery is in place.
