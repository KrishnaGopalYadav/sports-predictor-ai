"""Registry for sport capabilities without coupling sport domains together.

The registry is deliberately metadata-only in this increment. Cricket and football
ingestion, feature engineering and model implementations remain independent modules
that can be registered as they are implemented.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable


@dataclass(frozen=True, slots=True)
class SportDefinition:
    """Stable platform-level identity and display metadata for a sport."""

    code: str
    display_name: str

    def __post_init__(self) -> None:
        normalized = self.code.strip().lower()
        if not normalized:
            raise ValueError("sport code must not be empty")
        if not self.display_name.strip():
            raise ValueError("sport display_name must not be empty")
        object.__setattr__(self, "code", normalized)


class SportRegistry:
    """In-memory registry that rejects duplicate sport codes."""

    def __init__(self, definitions: Iterable[SportDefinition] = ()) -> None:
        self._definitions: dict[str, SportDefinition] = {}
        for definition in definitions:
            self.register(definition)

    def register(self, definition: SportDefinition) -> None:
        if definition.code in self._definitions:
            raise ValueError(f"sport already registered: {definition.code}")
        self._definitions[definition.code] = definition

    def get(self, code: str) -> SportDefinition:
        key = code.strip().lower()
        try:
            return self._definitions[key]
        except KeyError as exc:
            raise KeyError(f"unsupported sport: {key}") from exc

    def list(self) -> list[SportDefinition]:
        return sorted(self._definitions.values(), key=lambda item: item.code)

    def supports(self, code: str) -> bool:
        return code.strip().lower() in self._definitions


def build_default_registry() -> SportRegistry:
    """Return the sports enabled for the initial product scope."""
    return SportRegistry(
        [
            SportDefinition(code="cricket", display_name="Cricket"),
            SportDefinition(code="football", display_name="Football"),
        ]
    )
