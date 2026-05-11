import re
from datetime import datetime as DateTime

from pydantic import BaseModel, Field, field_validator

from app.skills.base import NoOpSkill

_CRON_FIELD_RE = re.compile(
    r"^(\*|\*/\d+|\d+(-\d+)?(,\d+(-\d+)?)*(\/\d+)?)$"
)


class RecurrentReminderForm(BaseModel):
    message: str = Field(description="What to remind about")
    cron: str = Field(description="Recurrence as a cron expression, e.g. '0 9 * * 1' for every Monday at 9am")
    start_date: str | None = Field(None, description="When to start the recurrence, in ISO 8601 format")

    @field_validator("message")
    @classmethod
    def message_not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("must not be empty")
        return v

    @field_validator("cron")
    @classmethod
    def cron_is_valid(cls, v: str) -> str:
        fields = v.strip().split()
        if len(fields) != 5:
            raise ValueError("must have exactly 5 fields: minute hour day month weekday")
        for f in fields:
            if not _CRON_FIELD_RE.match(f):
                raise ValueError(f"invalid cron field: {f!r}")
        return v

    @field_validator("start_date")
    @classmethod
    def start_date_is_iso(cls, v: str | None) -> str | None:
        if v is None:
            return v
        try:
            DateTime.fromisoformat(v)
        except ValueError:
            raise ValueError("must be a valid ISO 8601 datetime string")
        return v


class RecurrentReminder(NoOpSkill):
    name = "recurrent_reminder"
    description = "Set a recurring reminder"
    form_model = RecurrentReminderForm
