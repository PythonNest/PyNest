---
description: Explain any PyNest concept with source-verified examples — modules, DI, guards, database providers, lifespan, decorators
allowedTools: Read, Bash
---

Announce at start: "Looking up PyNest internals to answer this."

You are explaining a PyNest concept. Never guess at internals — read the source first, then answer.

## Workflow

1. **Identify the concept** from the user's question (or the argument passed to this command).
2. **Read the relevant source** using the map below.
3. **Answer with this structure:**
   - One-sentence summary of what it does
   - How it works mechanically (what the decorator/class actually does, from the source you read)
   - Minimal working code example — complete, copy-pasteable, no `...` gaps
   - 2–3 concrete mistakes to avoid for this specific concept

## Source map

| Concept | Read these files |
|---|---|
| `@Module` wiring | `nest/core/decorators/module.py`, `nest/core/pynest_container.py` |
| `@Injectable` / DI | `nest/core/decorators/injectable.py`, `nest/core/decorators/utils.py` |
| `@Controller` / routing | `nest/core/decorators/controller.py`, `nest/core/decorators/http_method.py` |
| Guards / `@UseGuards` | `nest/core/decorators/guards.py` |
| Async ORM (Postgres) | `nest/core/database/orm_provider.py`, `nest/core/database/orm_config.py` |
| MongoDB (Beanie) | `nest/core/database/odm_provider.py`, `nest/core/database/odm_config.py` |
| App bootstrap | `nest/core/pynest_factory.py`, `nest/core/pynest_application.py` |
| Lifespan / startup tasks | `nest/core/pynest_application.py` |
| Module exports / imports | `nest/common/module.py`, `nest/core/pynest_container.py` |
| CLI generate | `nest/cli/cli.py`, `nest/cli/click_handlers.py` |

If the concept spans multiple files, read all relevant ones before answering.

## Rules

- Never invent API surface. If a method or param isn't in the source, say it doesn't exist.
- If the source and the docs disagree, trust the source and note the discrepancy.
- Keep code examples under 40 lines.
- Match async/sync style to what the user's codebase uses (check `src/app_module.py` if unsure).
