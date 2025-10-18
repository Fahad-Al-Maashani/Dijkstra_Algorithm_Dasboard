# Dijkstra Adventure Simulator

An interactive Python experience that visualizes classic shortest-path algorithms in a neon-styled traversal game. Pilot a pathfinding drone across curated maps, compare multiple algorithms side by side, and celebrate the optimal route with cinematic fly-throughs and exportable artefacts.

## Highlights

- Guided scenarios that preconfigure levels, start/goal nodes, and recommended algorithms.
- Algorithm switcher supporting Dijkstra, A*, and Bellman-Ford with step-by-step playback.
- Graph editor for adding/removing nodes, tweaking edge weights, and dragging layouts in real time.
- Achievement tracking to encourage experimentation, plus contextual tooltips for every control.
- Export run data as structured JSON or render the animation as an animated GIF (optional Pillow dependency).

## Requirements

- Python 3.10 or newer (only standard-library modules are used)

## How to Run

```bash
python main.py
```

The window opens with the **Cyber Grid** level selected. Choose a start and goal node (or pick a guided scenario), select an algorithm, then launch the simulation.

## Controls

- **Scenario selector**: Load themed missions that pre-set start/goal nodes and suggested algorithms.
- **Pick Start / Pick Goal** radio buttons: Decide which node role to assign before clicking a node on the canvas.
- **Algorithm chooser**: Toggle between Dijkstra, A*, and Bellman-Ford before running.
- **Run Simulation**: Plays the animation from start to finish.
- **Step**: Advances the algorithm one state at a time.
- **Reset**: Clears the current run and restores node colors.
- **Randomize Weights**: Refreshes edge weights to produce new routes.
- **Swap Start/Goal**: Swaps endpoints without changing the level.
- **Compare Algorithms**: Runs all algorithms and summarises cost + step counts.
- **Export JSON/GIF**: Save the current run (Pillow required for GIF export).
- **Animation Speed**: Drag to slow down or accelerate the visualization.
- **Zoom Controls** (overlay on the canvas): Use the slider, buttons, or mouse wheel to zoom in/out while editing or observing the graph.

### Editing Mode

Toggle **Enable Edit Mode** to access graph editing actions:

- **Add/Remove Node**: Click on the canvas or select nodes to modify the layout.
- **Add/Remove Edge** / **Set Weight**: Click the two endpoints to create, delete, or adjust connections.
- Drag nodes directly on the canvas to reposition them.
- Hover over any control to see contextual instructions.

### Live Telemetry

As the algorithm runs, the sidebar keeps you informed with:

- Current node being visited
- Frontier size and relaxed edges
- Up-to-date distance table
- Final path description and total cost

Achievements update automatically (First Run, Algorithm Explorer, Efficiency Star), and tooltips describe every control on hover.

Once the shortest path is found, a glowing drone traces the optimal route across the map. Use the export buttons to capture the experience or share the underlying data.
