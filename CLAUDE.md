# agent-api

FastAPI service that exposes "skills" — structured actions invoked from natural language. Part of a WhatsApp personal assistant stack (Evolution API → n8n → this API).

## How it works

1. Caller sends `POST /skills/{skill_name}/invoke` with a free-text `user_input`
2. Gemini extracts fields via function calling (all fields treated as optional at extraction time)
3. Pydantic validates the extracted dict against the skill's form model (required fields enforced here)
4. Returns `complete` with the skill's result, or `invalid` with a list of field-level errors

## Project structure

```
app/
├── main.py          # FastAPI app, lifespan, two endpoints: GET /skills, POST /skills/{name}/invoke
├── registry.py      # Auto-discovers skill classes from app/skills/ at startup
├── models.py        # Wire protocol: InvokeRequest, InvokeResponse, FieldError, SkillInfo
├── llm.py           # Gemini client — calls function_declaration().model_dump() and extracts args
└── skills/
    ├── base.py      # BaseSkill ABC + GeminiFunctionDeclaration DTOs + field_to_gemini_schema()
    ├── create_google_task.py
    └── update_google_task.py
```

## Adding a skill

Drop a new file in `app/skills/`. The registry picks it up automatically on next startup — no other changes needed.

Each skill file must define:
- A Pydantic form model (required fields declared without defaults, optional with `... | None = None`)
- A class that extends `BaseSkill` with `name`, `description`, `form_model` class vars and an `execute()` method

```python
from pydantic import BaseModel, Field
from app.skills.base import BaseSkill

class MyActionForm(BaseModel):
    required_field: str = Field(description="...")
    optional_field: str | None = Field(None, description="...")

class MyAction(BaseSkill):
    name = "my_action"
    description = "Does something useful"
    form_model = MyActionForm

    async def execute(self, form: MyActionForm) -> dict:
        # integration logic here
        return {"status": "done"}
```

## Key design decisions

- **All fields optional in the Gemini schema** (`required: []` always) — prevents the LLM from hallucinating values for missing fields. Required vs optional is enforced by Pydantic after extraction.
- **`field_to_gemini_schema()` unwraps `X | None`** — Gemini doesn't support `anyOf`, so union types are simplified to their non-null branch before building the schema.
- **`GeminiFunctionDeclaration` is a DTO** — `function_declaration()` returns a typed Pydantic model; `llm.py` calls `.model_dump(exclude_none=True)` when passing it to the SDK.
- **Registry uses `pkgutil.iter_modules`** — scans `app/skills/` at startup, instantiates any class that subclasses `BaseSkill`.
- **Stateless API** — no session storage. If multi-turn form filling is added later, the caller owns state and echoes it back via `partial_form`.

## Environment variables

| Variable | Description |
|---|---|
| `GEMINI_API_KEY` | Google Gemini API key |

## Deployment

Built and deployed from this repo via the `nucbox-g3-docker` orchestration repo:

```bash
# On the homelab server (192.168.0.100)
cd ~/nucbox-g3-docker/agent-api
docker compose --env-file ../.env up --build -d
```

The `docker-compose.yml` in `nucbox-g3-docker/agent-api/` builds from this GitHub repo directly (`build: https://github.com/damif94/agent-api.git`), so pushing to `master` is enough — next `up --build` picks it up.

Port: `8090` → container `8000`. Swagger UI at `http://192.168.0.100:8090/docs`.
