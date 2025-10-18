from __future__ import annotations

import math
from dataclasses import dataclass
from heapq import heappop, heappush
from itertools import count
from math import inf, sqrt
from typing import Dict, List, Optional, Tuple

from .graph import WeightedGraph


@dataclass
class PathStep:
    """Snapshot of a pathfinding algorithm's state."""

    current: Optional[str]
    distances: Dict[str, float]
    visited: List[str]
    frontier: List[Tuple[str, float]]
    previous: Dict[str, str]
    relaxed_edge: Optional[Tuple[str, str]] = None
    iteration: Optional[int] = None
    notes: Optional[str] = None


@dataclass
class PathResult:
    """Aggregate outcome of a pathfinding run."""

    path: List[str]
    cost: float
    steps: List[PathStep]
    algorithm: str
    negative_cycle: bool = False


class ExplorerBase:
    """Common utilities shared across explorers."""

    def __init__(self, graph: WeightedGraph) -> None:
        self.graph = graph

    @staticmethod
    def _build_step(
        current: Optional[str],
        visited: List[str],
        frontier: List[Tuple[str, float]],
        distances: Dict[str, float],
        previous: Dict[str, str],
        relaxed_edge: Optional[Tuple[str, str]] = None,
        iteration: Optional[int] = None,
        notes: Optional[str] = None,
    ) -> PathStep:
        snapshot = sorted(frontier, key=lambda item: item[1])
        return PathStep(
            current=current,
            visited=list(visited),
            frontier=snapshot,
            distances=dict(distances),
            previous=dict(previous),
            relaxed_edge=relaxed_edge,
            iteration=iteration,
            notes=notes,
        )

    @staticmethod
    def _reconstruct_path(previous: Dict[str, str], start: str, goal: str) -> List[str]:
        if goal not in previous and goal != start:
            return []
        path: List[str] = [goal]
        current = goal
        while current != start:
            current = previous.get(current)
            if current is None:
                return []
            path.append(current)
        path.reverse()
        return path

    @staticmethod
    def _fmt(value: float) -> str:
        number = float(value)
        if math.isnan(number):
            return "nan"
        if math.isinf(number):
            return "∞"
        return f"{number:.0f}" if number.is_integer() else f"{number:.2f}"


class DijkstraExplorer(ExplorerBase):
    """Classic Dijkstra's algorithm with state capture."""

    def run(self, start: str, goal: str) -> PathResult:
        if start not in self.graph.nodes or goal not in self.graph.nodes:
            raise ValueError("Start or goal node not present in graph.")

        distances: Dict[str, float] = {node: inf for node in self.graph.nodes}
        previous: Dict[str, str] = {}
        visited: List[str] = []
        heap: List[Tuple[float, str]] = []

        distances[start] = 0.0
        heappush(heap, (0.0, start))

        steps: List[PathStep] = [
            self._build_step(
                current=None,
                visited=visited,
                frontier=[(node, dist) for dist, node in heap],
                distances=distances,
                previous=previous,
                iteration=0,
                notes="Initialized frontier with the start node.",
            )
        ]

        iteration = 0
        while heap:
            distance, node_id = heappop(heap)
            if node_id in visited:
                continue

            visited.append(node_id)
            iteration += 1
            steps.append(
                self._build_step(
                    current=node_id,
                    visited=visited,
                    frontier=[(node, dist) for dist, node in heap if node not in visited],
                    distances=distances,
                    previous=previous,
                    relaxed_edge=None,
                    iteration=iteration,
                    notes=f"Processing node {node_id} with distance {self._fmt(distance)}.",
                )
            )

            if node_id == goal:
                break

            for neighbor_id, weight in self.graph.neighbors(node_id).items():
                tentative = distance + weight
                if tentative < distances[neighbor_id]:
                    distances[neighbor_id] = tentative
                    previous[neighbor_id] = node_id
                    heappush(heap, (tentative, neighbor_id))
                    steps.append(
                        self._build_step(
                            current=node_id,
                            visited=visited,
                            frontier=[(node, dist) for dist, node in heap if node not in visited],
                            distances=distances,
                            previous=previous,
                            relaxed_edge=(node_id, neighbor_id),
                            iteration=iteration,
                            notes=f"Relaxed {node_id}→{neighbor_id} to {self._fmt(tentative)}.",
                        )
                    )

        path = self._reconstruct_path(previous, start, goal)
        cost = distances[goal]
        return PathResult(path=path, cost=cost, steps=steps, algorithm="Dijkstra")


class AStarExplorer(ExplorerBase):
    """A* search with Euclidean heuristic based on node layout."""

    def __init__(self, graph: WeightedGraph) -> None:
        super().__init__(graph)
        weights = [weight for _, _, weight in graph.edges()]
        self.heuristic_scale = sum(weights) / len(weights) if weights else 1.0

    def run(self, start: str, goal: str) -> PathResult:
        if start not in self.graph.nodes or goal not in self.graph.nodes:
            raise ValueError("Start or goal node not present in graph.")

        g_score: Dict[str, float] = {node: inf for node in self.graph.nodes}
        f_score: Dict[str, float] = {node: inf for node in self.graph.nodes}
        previous: Dict[str, str] = {}

        g_score[start] = 0.0
        f_start = self._heuristic(start, goal)
        f_score[start] = f_start

        open_heap: List[Tuple[float, int, str]] = []
        counter = count()
        heappush(open_heap, (f_start, next(counter), start))

        closed: set[str] = set()
        visited_order: List[str] = []

        steps: List[PathStep] = [
            self._build_step(
                current=None,
                visited=visited_order,
                frontier=[(start, f_start)],
                distances=g_score,
                previous=previous,
                iteration=0,
                notes=f"Initialized with heuristic cost {self._fmt(f_start)}.",
            )
        ]

        while open_heap:
            current_f, _, node_id = heappop(open_heap)
            if node_id in closed:
                continue

            closed.add(node_id)
            visited_order.append(node_id)
            frontier_snapshot = [(n, f_score[n]) for _, _, n in open_heap if n not in closed]

            steps.append(
                self._build_step(
                    current=node_id,
                    visited=visited_order,
                    frontier=frontier_snapshot,
                    distances=g_score,
                    previous=previous,
                    relaxed_edge=None,
                    iteration=len(visited_order),
                    notes=f"Exploring node {node_id} with f={self._fmt(current_f)}.",
                )
            )

            if node_id == goal:
                break

            for neighbor_id, weight in self.graph.neighbors(node_id).items():
                tentative_g = g_score[node_id] + weight
                if tentative_g < g_score[neighbor_id]:
                    previous[neighbor_id] = node_id
                    g_score[neighbor_id] = tentative_g
                    h = self._heuristic(neighbor_id, goal)
                    f_total = tentative_g + h
                    f_score[neighbor_id] = f_total
                    heappush(open_heap, (f_total, next(counter), neighbor_id))
                    frontier_snapshot = [(n, f_score[n]) for _, _, n in open_heap if n not in closed]
                    steps.append(
                        self._build_step(
                            current=node_id,
                            visited=visited_order,
                            frontier=frontier_snapshot,
                            distances=g_score,
                            previous=previous,
                            relaxed_edge=(node_id, neighbor_id),
                            iteration=len(visited_order),
                            notes=f"Relaxed {node_id}→{neighbor_id} (g={self._fmt(tentative_g)}, h={self._fmt(h)}).",
                        )
                    )

        path = self._reconstruct_path(previous, start, goal)
        cost = g_score[goal]
        return PathResult(path=path, cost=cost, steps=steps, algorithm="A*")

    def _heuristic(self, node_id: str, goal_id: str) -> float:
        node_pos = self.graph.nodes[node_id].position
        goal_pos = self.graph.nodes[goal_id].position
        dx = node_pos[0] - goal_pos[0]
        dy = node_pos[1] - goal_pos[1]
        return sqrt(dx * dx + dy * dy) * self.heuristic_scale


class BellmanFordExplorer(ExplorerBase):
    """Bellman-Ford implementation with iteration snapshots."""

    def run(self, start: str, goal: str) -> PathResult:
        if start not in self.graph.nodes or goal not in self.graph.nodes:
            raise ValueError("Start or goal node not present in graph.")

        distances: Dict[str, float] = {node: inf for node in self.graph.nodes}
        previous: Dict[str, str] = {}
        distances[start] = 0.0

        steps: List[PathStep] = [
            self._build_step(
                current=None,
                visited=[],
                frontier=[],
                distances=distances,
                previous=previous,
                iteration=0,
                notes="Initialization complete.",
            )
        ]

        nodes = list(self.graph.nodes.keys())
        edges = list(self.graph.edges())
        last_iteration = 0

        for iteration in range(1, len(nodes)):
            updated_this_round: List[str] = []
            changed = False
            for source, target, weight in edges:
                if math.isinf(distances[source]):
                    continue
                new_distance = distances[source] + weight
                if new_distance < distances[target]:
                    distances[target] = new_distance
                    previous[target] = source
                    updated_this_round.append(target)
                    changed = True
                    steps.append(
                        self._build_step(
                            current=source,
                            visited=list(dict.fromkeys(updated_this_round)),
                            frontier=[],
                            distances=distances,
                            previous=previous,
                            relaxed_edge=(source, target),
                            iteration=iteration,
                            notes=f"Iteration {iteration}: relaxed {source}→{target} to {self._fmt(new_distance)}.",
                        )
                    )
            if not changed:
                break
            last_iteration = iteration

        negative_cycle = False
        for source, target, weight in edges:
            if math.isinf(distances[source]):
                continue
            if distances[source] + weight < distances[target]:
                negative_cycle = True
                steps.append(
                    self._build_step(
                        current=source,
                        visited=[],
                        frontier=[],
                        distances=distances,
                        previous=previous,
                        relaxed_edge=(source, target),
                        iteration=last_iteration + 1,
                        notes="Negative cycle detected affecting reachable nodes.",
                    )
                )
                break

        path = [] if negative_cycle else self._reconstruct_path(previous, start, goal)
        cost = distances[goal]
        return PathResult(path=path, cost=cost, steps=steps, algorithm="Bellman-Ford", negative_cycle=negative_cycle)
