# PyNest CLI

The PyNest CLI scaffolds applications and common application components. The primary command surface is:

```bash
pynest new my_app
pynest add resource users
pynest add gateway chat
pynest doctor
```

Older `pynest generate ...` commands still work for compatibility.

## Install

```bash
pip install pynest-api
```

## Create An Application

For a guided human flow:

```bash
pynest new --prompt
```

For a direct command:

```bash
pynest new my_app
```

For an agent or script:

```bash
pynest new my_app --preset api --database sqlite --async --yes --json
```

Useful options:

- `--preset api|cli`: choose an HTTP API app or CLI app. Default: `api`.
- `--database none|sqlite|postgresql|mysql|mongodb`: add database scaffolding. Default: `none`.
- `--async`: use async database access for relational databases.
- `--path PATH`: parent directory where the app should be created.
- `--package-manager uv|requirements`: choose generated dependency files. Default: `uv`.
- `--prompt`: force guided prompts.
- `--yes`: accept defaults and skip prompts.
- `--dry-run`: show the plan without writing files.
- `--json`: emit machine-readable JSON only.
- `--quiet`: suppress human output.
- `--force`: overwrite supported files.

Generated API apps include:

```text
my_app/
├── .pynest.yaml
├── main.py
├── README.md
├── pyproject.toml
└── src/
    ├── __init__.py
    ├── app_module.py
    ├── app_controller.py
    └── app_service.py
```

Database apps also include `src/config.py`, `.env.example`, and database-specific requirements.

PyNest uses `uv` by default and writes `pyproject.toml`. Use `--package-manager requirements` only when you need a legacy `requirements.txt` workflow.

Prompt mode also asks for package management:

```text
Package manager:
  1. uv
  2. requirements.txt
Choose package manager [1]:
```

## Add Components

Run these commands inside a PyNest application, or pass `--path` to the app root.

```bash
pynest add resource users
pynest add module auth
pynest add controller users
pynest add service users
pynest add gateway chat
```

Shared options:

- `--path PATH`: target app or source directory.
- `--dry-run`: show the plan without writing files.
- `--json`: emit machine-readable JSON only.
- `--quiet`: suppress human output.
- `--force`: overwrite supported files.

`pynest add` reads `.pynest.yaml` so generated resources match the app preset, database, and async settings.

`pynest add gateway <name>` creates a small package under `src/<name>/` (`__init__.py`, `<name>_gateway.py`, `<name>_module.py` with the gateway in `providers`), and registers `<Name>Module` in `src/app_module.py` — same pattern as `add resource`, without HTTP CRUD files.

## Check A Project

```bash
pynest doctor
```

`doctor` checks project metadata and source layout. For agents:

```bash
pynest doctor --json
```

## Compatibility Commands

These commands are still supported:

```bash
pynest generate application -n my_app
pynest generate resource -n users
pynest generate module -n auth
pynest generate controller -n users
pynest generate service -n users
pynest generate gateway -n chat
```

Compatibility commands also support `--json` and `--dry-run` where applicable.

---
<nav class="md-footer-nav">
  <a href="/PyNest/getting_started" class="md-footer-nav__link">
    <span>&larr; Getting Started</span>
  </a>
  <a href="/PyNest/modules" class="md-footer-nav__link">
    <span>Modules &rarr;</span>
  </a>
</nav>
