from datetime import datetime as DateTime

from pydantic import BaseModel, Field, field_validator

from app.skills.base import NoOpSkill


class AdHocReminderForm(BaseModel):
    message: str = Field(description="What to remind about")
    datetime: str = Field(description="When to trigger the reminder, in ISO 8601 format")

    @field_validator("message")
    @classmethod
    def message_not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("must not be empty")
        return v

    @field_validator("datetime")
    @classmethod
    def datetime_is_iso(cls, v: str) -> str:
        try:
            DateTime.fromisoformat(v)
        except ValueError:
            raise ValueError("must be a valid ISO 8601 datetime string")
        return v


class AdHocReminder(NoOpSkill):
    name = "adhoc_reminder"
    description = "Set a one-time reminder"
    form_model = AdHocReminderForm
