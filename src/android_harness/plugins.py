"""Plugin registry for optional Android Harness capabilities."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable


Capability = Callable[..., Any]


@dataclass
class PluginRegistry:
    actions: dict[str, Capability] = field(default_factory=dict)
    detectors: dict[str, Capability] = field(default_factory=dict)
    policies: dict[str, Capability] = field(default_factory=dict)
    environment: dict[str, Capability] = field(default_factory=dict)

    def register_action(self, name: str, fn: Capability) -> None:
        self.actions[name] = fn

    def register_detector(self, name: str, fn: Capability) -> None:
        self.detectors[name] = fn

    def register_policy(self, name: str, fn: Capability) -> None:
        self.policies[name] = fn

    def register_environment(self, name: str, fn: Capability) -> None:
        self.environment[name] = fn

    def capabilities(self) -> dict[str, list[str]]:
        return {
            "actions": sorted(self.actions),
            "detectors": sorted(self.detectors),
            "policies": sorted(self.policies),
            "environment": sorted(self.environment),
        }


registry = PluginRegistry()
