from __future__ import annotations

import importlib
import pkgutil

import app.skills as skills_pkg
from app.skills.base import BaseSkill, NoOpSkill

_registry: dict[str, BaseSkill] = {}


def load() -> None:
    for _, module_name, _ in pkgutil.iter_modules(skills_pkg.__path__):
        if module_name == "base":
            continue
        mod = importlib.import_module(f"app.skills.{module_name}")
        for attr in vars(mod).values():
            if (
                isinstance(attr, type)
                and issubclass(attr, BaseSkill)
                and attr is not BaseSkill
                and attr is not NoOpSkill
            ):
                instance = attr()
                _registry[instance.name] = instance


def get(name: str) -> BaseSkill | None:
    return _registry.get(name)


def all_skills() -> list[BaseSkill]:
    return list(_registry.values())
