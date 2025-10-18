from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterable, List

from .graph import EdgeSpec, NodeInfo, WeightedGraph


@dataclass(frozen=True)
class Level:
    """Preset playable graph configuration."""

    name: str
    description: str
    nodes: Dict[str, NodeInfo]
    edges: List[EdgeSpec]
    default_start: str
    default_goal: str

    def build_graph(self) -> WeightedGraph:
        return WeightedGraph(self.nodes, self.edges)


def _cyber_grid() -> Level:
    nodes = {
        "A": NodeInfo("Alpha Station", (0.08, 0.72)),
        "B": NodeInfo("Beacon Ridge", (0.22, 0.42)),
        "C": NodeInfo("Circuit Gate", (0.42, 0.22)),
        "D": NodeInfo("Drone Docks", (0.58, 0.48)),
        "E": NodeInfo("Emitter Row", (0.78, 0.3)),
        "F": NodeInfo("Flux Harbor", (0.76, 0.7)),
        "G": NodeInfo("Gateway Hub", (0.55, 0.87)),
        "H": NodeInfo("Horizon Node", (0.3, 0.86)),
    }
    edges = [
        EdgeSpec("A", "B", 6),
        EdgeSpec("A", "H", 5),
        EdgeSpec("B", "C", 4),
        EdgeSpec("B", "D", 7),
        EdgeSpec("C", "D", 3),
        EdgeSpec("C", "E", 5),
        EdgeSpec("D", "E", 2),
        EdgeSpec("D", "F", 6),
        EdgeSpec("D", "G", 4),
        EdgeSpec("E", "F", 3),
        EdgeSpec("F", "G", 2),
        EdgeSpec("G", "H", 4),
        EdgeSpec("H", "B", 6),
    ]

    return Level(
        name="Cyber Grid",
        description="Navigate neon rooftops atop a cyberpunk skyline.",
        nodes=nodes,
        edges=edges,
        default_start="A",
        default_goal="F",
    )


def _mountain_pass() -> Level:
    nodes = {
        "S": NodeInfo("Summit Camp", (0.12, 0.18)),
        "T": NodeInfo("Tundra Lift", (0.3, 0.35)),
        "U": NodeInfo("Upper Crag", (0.48, 0.2)),
        "V": NodeInfo("Valley Rest", (0.65, 0.32)),
        "W": NodeInfo("Windy Ridge", (0.82, 0.18)),
        "X": NodeInfo("Crosswind Gate", (0.74, 0.56)),
        "Y": NodeInfo("Yodel Peak", (0.5, 0.65)),
        "Z": NodeInfo("Zenith Base", (0.3, 0.62)),
        "R": NodeInfo("River Fork", (0.15, 0.52)),
    }
    edges = [
        EdgeSpec("S", "T", 3),
        EdgeSpec("T", "U", 2),
        EdgeSpec("U", "V", 4),
        EdgeSpec("V", "W", 6),
        EdgeSpec("W", "X", 3),
        EdgeSpec("X", "Y", 4),
        EdgeSpec("Y", "Z", 5),
        EdgeSpec("Z", "R", 4),
        EdgeSpec("R", "S", 2),
        EdgeSpec("T", "Z", 7),
        EdgeSpec("U", "Y", 6),
        EdgeSpec("V", "Y", 5),
        EdgeSpec("X", "V", 2),
    ]

    return Level(
        name="Mountain Pass",
        description="Guide a rescue drone through icy ridges and lift towers.",
        nodes=nodes,
        edges=edges,
        default_start="S",
        default_goal="X",
    )


def _cosmic_orbit() -> Level:
    nodes = {
        "C1": NodeInfo("Comet Dock", (0.1, 0.5)),
        "C2": NodeInfo("Crater Hub", (0.23, 0.26)),
        "C3": NodeInfo("Crystal Array", (0.4, 0.12)),
        "C4": NodeInfo("Core Reactor", (0.63, 0.15)),
        "C5": NodeInfo("Command Spire", (0.82, 0.35)),
        "C6": NodeInfo("Cargo Ring", (0.88, 0.62)),
        "C7": NodeInfo("Containment Bay", (0.68, 0.82)),
        "C8": NodeInfo("Catalyst Pod", (0.42, 0.88)),
        "C9": NodeInfo("Chrono Lab", (0.22, 0.76)),
        "C10": NodeInfo("Celestial Gate", (0.5, 0.5)),
    }
    edges = [
        EdgeSpec("C1", "C2", 4),
        EdgeSpec("C2", "C3", 6),
        EdgeSpec("C3", "C4", 5),
        EdgeSpec("C4", "C5", 3),
        EdgeSpec("C5", "C6", 4),
        EdgeSpec("C6", "C7", 3),
        EdgeSpec("C7", "C8", 4),
        EdgeSpec("C8", "C9", 6),
        EdgeSpec("C9", "C1", 5),
        EdgeSpec("C2", "C10", 7),
        EdgeSpec("C3", "C10", 4),
        EdgeSpec("C4", "C10", 6),
        EdgeSpec("C5", "C10", 5),
        EdgeSpec("C6", "C10", 7),
        EdgeSpec("C7", "C10", 5),
        EdgeSpec("C8", "C10", 4),
        EdgeSpec("C9", "C10", 3),
        EdgeSpec("C1", "C10", 8),
    ]

    return Level(
        name="Cosmic Orbit",
        description="Run supply routes between floating orbital platforms.",
        nodes=nodes,
        edges=edges,
        default_start="C1",
        default_goal="C6",
    )


def get_levels() -> Iterable[Level]:
    yield _cyber_grid()
    yield _mountain_pass()
    yield _cosmic_orbit()
