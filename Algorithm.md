# Dijkstra Adventure Simulator – Algorithm Notes

## Reference Graph

The simulator ships with three presets. The default **Cyber Grid** level is described by the following weighted, undirected graph:

| Edge | Weight |
|------|--------|
| A–B  | 6      |
| A–H  | 5      |
| B–C  | 4      |
| B–D  | 7      |
| C–D  | 3      |
| C–E  | 5      |
| D–E  | 2      |
| D–F  | 6      |
| D–G  | 4      |
| E–F  | 3      |
| F–G  | 2      |
| G–H  | 4      |
| H–B  | 6      |

Positions used in the GUI correspond to normalized coordinates; the edge list above captures the full mathematical structure consumed by the algorithm.

## Dijkstra’s Algorithm Recap

Given a weighted graph \( G = (V, E) \) with non‑negative edge weights \( w : E \rightarrow \mathbb{R}_{\ge 0} \), Dijkstra’s algorithm computes shortest-path distances from a start vertex \( s \in V \) to all other vertices.

### Initialization

- \( \mathrm{dist}[v] = \infty \) for all \( v \in V \setminus \{s\} \)
- \( \mathrm{dist}[s] = 0 \)
- `previous[v] = undefined`
- Priority queue \( Q \) seeded with \( (0, s) \)

This mirrors the implementation in `dijkstra_game/graph.py:111-118`.

### Invariant

At each iteration, the queue contains frontier vertices whose current key equals their best-known tentative distance. The algorithm repeatedly extracts the minimum-distance vertex \( u \) and “settles” it. Once removed from \( Q \), \( \mathrm{dist}[u] \) is provably equal to the true shortest-path distance \( \delta(s, u) \). This invariant holds because every edge weight is non-negative, guaranteeing that any alternative path to \( u \) discovered later through yet-unsettled vertices must have length at least \( \mathrm{dist}[u] \).

### Relaxation Step

For each neighbor \( v \) of the settled vertex \( u \), the algorithm computes a candidate distance:

\[
\text{alt} = \mathrm{dist}[u] + w(u, v).
\]

If \( \text{alt} < \mathrm{dist}[v] \), then we update:

\[
\mathrm{dist}[v] \leftarrow \text{alt}, \quad \text{previous}[v] \leftarrow u,
\]

and push \( ( \text{alt}, v ) \) back into the priority queue. This exactly matches the relaxation code at `dijkstra_game/graph.py:150-164`.

### Termination and Path Reconstruction

The loop continues until the queue is empty or the goal vertex \( g \) is settled. The shortest path is reconstructed by following the `previous` map backwards from \( g \) to \( s \). If \( g \) was never assigned a predecessor (and \( g \neq s \)), then no path exists. See `dijkstra_game/graph.py:191-199`.

## Correctness Sketch

1. **Non-negativity**: All simulator edges satisfy \( w(u, v) \ge 0 \). Randomized weights are constrained to integers in \([2, 12]\), ensuring the invariant remains valid.
2. **Monotonic Extraction**: The priority queue always extracts either a freshly discovered vertex or a duplicate entry for a vertex already marked visited. Duplicates are ignored (`dijkstra_game/graph.py:131-133`), so each vertex is settled exactly once.
3. **Shortest Distance Guarantee**: Suppose \( u \) is the next vertex removed from the queue. Any alternate path to \( u \) would have to pass through another unsettled vertex \( x \) with tentative distance at least \( \mathrm{dist}[x] \ge \mathrm{dist}[u] \). Therefore \( \mathrm{dist}[u] \) is the minimum achievable, proving by induction on extraction order that \( \mathrm{dist}[u] = \delta(s,u) \).

Combining these points yields the standard proof of Dijkstra’s correctness.

## Complexity

Let \( n = |V| \) and \( m = |E| \).

- Using a binary heap, each `heappush` and `heappop` costs \( O(\log n) \).
- Each vertex is extracted exactly once; each edge triggers at most one relaxation test.

Thus the overall time complexity is \( O((n + m) \log n) \), and the simulator’s state capture only adds constant overhead per relaxation to store snapshots for animation.

## A* Search (Heuristic Mode)

The simulator’s A* implementation shares Dijkstra’s mechanics but augments each node with an admissible heuristic. The heuristic is the Euclidean distance between node layouts (normalised to \([0,1]\)) scaled by the mean edge weight of the current graph. For any nodes \( u, v \):

\[
h(u) = \operatorname{avg}(w) \cdot \sqrt{(x_u - x_v)^2 + (y_u - y_v)^2}
\]

Because edge weights are non-negative, this heuristic never overestimates the true remaining cost, so A* preserves optimality while typically expanding fewer nodes.

During each expansion the simulator records:

- `f = g + h` for the node extracted from the open set,
- the updated frontier with the new priority values,
- the relaxed edge and concatenated notes to explain each change.

Complexity remains \( O((n + m) \log n) \), but the guided expansions often reduce the effective number of operations.

## Bellman-Ford

Bellman-Ford iteratively relaxes every edge \( |V| - 1 \) times, which guarantees shortest paths even when edges carry negative weights (the editor keeps weights positive by default, but the implementation is general). The simulator captures a snapshot whenever an edge improves a distance:

- `iteration` in the step payload records the current pass number,
- `visited` lists the nodes updated in the present iteration, providing a visual cue for propagation.

After the relaxation passes, the simulator performs one additional sweep to flag a negative cycle; when detected, the final frame is annotated and the path is marked undefined.

The algorithm runs in \( O(nm) \) time and \( O(n) \) space. Despite the higher complexity, providing this view alongside Dijkstra and A* offers a powerful comparative teaching aid.
