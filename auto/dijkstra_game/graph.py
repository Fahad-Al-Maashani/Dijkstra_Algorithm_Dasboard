from __future__ import annotations

from dataclasses import dataclass
import random
from typing import Dict, Iterable, Iterator, Tuple


@dataclass(frozen=True)
class NodeInfo:
    """Lightweight description for a drawable node."""

    label: str
    position: Tuple[float, float]


@dataclass(frozen=True)
class EdgeSpec:
    """Description of an undirected weighted connection."""

    source: str
    target: str
    weight: float


class WeightedGraph:
    """Simple undirected weighted graph tailored for the simulator."""

    def __init__(self, nodes: Dict[str, NodeInfo], edges: Iterable[EdgeSpec]) -> None:
        self.nodes: Dict[str, NodeInfo] = dict(nodes)
        self._adjacency: Dict[str, Dict[str, float]] = {node_id: {} for node_id in nodes}
        self._edge_data: Dict[Tuple[str, str], float] = {}
        for edge in edges:
            self.add_edge(edge.source, edge.target, edge.weight)

    # ---------------------------- mutation helpers ------------------------- #
    def add_node(self, node_id: str, label: str, position: Tuple[float, float]) -> None:
        if node_id in self.nodes:
            raise ValueError(f"Node '{node_id}' already exists.")
        self.nodes[node_id] = NodeInfo(label=label, position=position)
        self._adjacency[node_id] = {}

    def remove_node(self, node_id: str) -> None:
        if node_id not in self.nodes:
            raise ValueError(f"Node '{node_id}' does not exist.")
        for neighbor in list(self._adjacency[node_id].keys()):
            self.remove_edge(node_id, neighbor)
        del self._adjacency[node_id]
        del self.nodes[node_id]

    def add_edge(self, source: str, target: str, weight: float) -> None:
        if source not in self.nodes or target not in self.nodes:
            raise ValueError(f"Unknown node in edge: {source}->{target}")
        self._adjacency[source][target] = float(weight)
        self._adjacency[target][source] = float(weight)
        key = self._edge_key(source, target)
        self._edge_data[key] = float(weight)

    def remove_edge(self, source: str, target: str) -> None:
        if source not in self._adjacency or target not in self._adjacency[source]:
            raise ValueError(f"Edge '{source}-{target}' not present.")
        del self._adjacency[source][target]
        del self._adjacency[target][source]
        key = self._edge_key(source, target)
        if key in self._edge_data:
            del self._edge_data[key]

    def neighbors(self, node_id: str) -> Dict[str, float]:
        return self._adjacency[node_id]

    def edge_weight(self, source: str, target: str) -> float:
        return self._adjacency[source][target]

    def set_edge_weight(self, source: str, target: str, weight: float) -> None:
        self._adjacency[source][target] = float(weight)
        self._adjacency[target][source] = float(weight)
        key = self._edge_key(source, target)
        self._edge_data[key] = float(weight)

    def update_node_position(self, node_id: str, position: Tuple[float, float]) -> None:
        if node_id not in self.nodes:
            raise ValueError(f"Node '{node_id}' does not exist.")
        node = self.nodes[node_id]
        self.nodes[node_id] = NodeInfo(label=node.label, position=position)

    def update_node_label(self, node_id: str, label: str) -> None:
        if node_id not in self.nodes:
            raise ValueError(f"Node '{node_id}' does not exist.")
        node = self.nodes[node_id]
        self.nodes[node_id] = NodeInfo(label=label, position=node.position)

    def edges(self) -> Iterator[Tuple[str, str, float]]:
        for (source, target), weight in self._edge_data.items():
            yield source, target, weight

    def randomize_weights(self, minimum: int = 2, maximum: int = 12) -> None:
        if minimum <= 0 or maximum <= 0 or minimum > maximum:
            raise ValueError("Weight bounds must be positive and minimum <= maximum.")
        updated: Dict[Tuple[str, str], float] = {}
        for source, target in self._edge_data:
            weight = float(random.randint(minimum, maximum))
            self._adjacency[source][target] = weight
            self._adjacency[target][source] = weight
            updated[(source, target)] = weight
        self._edge_data.update(updated)

    def copy(self) -> "WeightedGraph":
        return WeightedGraph(self.nodes, (EdgeSpec(src, tgt, w) for src, tgt, w in self.edges()))

    @staticmethod
    def _edge_key(source: str, target: str) -> Tuple[str, str]:
        return tuple(sorted((source, target)))
