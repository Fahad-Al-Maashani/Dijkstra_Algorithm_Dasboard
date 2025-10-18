from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, List, Optional


@dataclass(frozen=True)
class Scenario:
    """Describes a guided mission with preset goals."""

    name: str
    description: str
    level_name: str
    start: str
    goal: str
    algorithm: Optional[str] = None


def get_scenarios() -> Iterable[Scenario]:
    """Return the curated set of guided missions."""
    yield Scenario(
        name="Neon Rescue",
        description="Use Dijkstra to deliver supplies across the cyber grid rooftops.",
        level_name="Cyber Grid",
        start="A",
        goal="F",
        algorithm="Dijkstra",
    )
    yield Scenario(
        name="Heuristic Dash",
        description="Harness A* to route a hovercraft between alpine outposts.",
        level_name="Mountain Pass",
        start="S",
        goal="X",
        algorithm="A*",
    )
    yield Scenario(
        name="Relay Run",
        description="Let Bellman-Ford manage routing across the orbital platforms.",
        level_name="Cosmic Orbit",
        start="C1",
        goal="C6",
        algorithm="Bellman-Ford",
    )
