from datetime import datetime as DateTime

from pydantic import BaseModel, Field, field_validator

from app.skills.base import NoOpSkill


class AdHocReminderForm(BaseModel):
    message: str = Field(description="What to remind about")
    datetime: str = Field(description="When to trigger the reminder, in ISO 8601 format (e.g. 2024-05-10T10:00:00). Only populate this field if the user explicitly states both a date AND a time. If the time is missing or ambiguous, omit this field entirely — do not assume or infer a default time.")

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
