"""Sport-specific extension points for Sports Predictor AI."""

from .registry import SportDefinition, SportRegistry, build_default_registry

__all__ = ["SportDefinition", "SportRegistry", "build_default_registry"]
