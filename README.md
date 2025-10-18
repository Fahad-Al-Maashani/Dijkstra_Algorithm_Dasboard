# Dijkstra Adventure Simulator

Bring shortest-path algorithms to life with an interactive, neon-styled dashboard.  
The simulator lets you **observe, edit, compare, and export** pathfinding runs across several curated maps – perfect for teaching, demos, and experimentation.

---

## ✨ Key Features

- **Algorithm Explorer** – switch between Dijkstra, A*, and Bellman–Ford at any moment, step through each state, or let the animation run automatically.
- **Graph Sandbox** – add/remove nodes, drag vertices freely, adjust edge weights, or randomize entire maps. Undo support (`⌘/Ctrl + Z`) keeps experimentation safe.
- **Guided Scenarios** – jump into themed missions with pre-configured start/goal pairs and recommended algorithms.
- **Live Telemetry** – watch distances, frontier membership, relaxed edges, and achievement streaks update in real time.
- **Presentation Ready** – zoomable canvas, cinematic drone fly-through on completion, and export options (JSON + optional GIF).

---

## 📦 Tech Snapshot

- **Language:** Python 3.10+
- **GUI Toolkit:** Tkinter (standard library)
- **Packaging:** None required – clone & run
- **Optional:** `Pillow` (for GIF export)

No external dependencies are needed for core functionality.

---

## 🚀 Quick Start

```bash
python main.py
```

The simulator boots into the **Cyber Grid** level. Choose start/goal nodes (or apply a scenario), select an algorithm, and hit **Run Simulation**.

### Recommended Workflow

1. Pick a level or scenario.
2. Toggle edit mode (optional) to tweak the graph layout.
3. Select the algorithm you want to visualize.
4. Step through or auto-run the simulation.
5. Export results or reset and iterate.

---

## 🧭 UI Reference

### Control Panel

- **Scenario Selector** – applies a themed mission with predefined start/goal/algorithm.
- **Node Role Pickers** – quickly mark any node as the start or goal.
- **Algorithm Switcher** – toggle between Dijkstra, A*, and Bellman–Ford on demand.
- **Run / Step / Reset** – animate an entire run, advance frame-by-frame, or reset the board.
- **Compare Algorithms** – benchmark all algorithms for the current start/goal with one click.
- **Randomize Weights / Swap Start & Goal** – generate fresh challenges instantly.
- **Export JSON / GIF** – persist detailed telemetry or share a looping animation (GIF requires `pip install pillow`).
- **Achievements** – track First Run, Algorithm Explorer, and Efficiency milestones.

### Graph Canvas

- **Drag & Drop Nodes** – every vertex is repositionable; edges adjust in real time.
- **Mouse Wheel / Slider / Buttons** – zoom in or out without losing context.
- **Right-Click Context Menus**
  - On canvas: add nodes, reset zoom, clear the graph.
  - On node: rename, delete, set as start/goal, create/remove edges, set weights.
- **Double-Click Canvas** – drop a new node instantly.
- **Undo (`⌘/Ctrl + Z`)** – revert the most recent graph change or reset.

### Editing Mode Highlights

- Action buttons (Add/Remove Node/Edge, Set Weight) tailor the next click(s).
- Tooltips guide every control.
- Path highlighting persists after simulations — final routes stay visible during edits or zoom operations.

---

## 🧪 Algorithm Telemetry

Each simulation captures a complete snapshot trail:

- Active node (`current`)
- Frontier membership (priority queue)
- Distance table
- Relaxed edge per step
- Iteration metrics (Bellman–Ford passes, A* `f` values)

Use **Export JSON** to archive these details programmatically, or **Export GIF** to share the animation (install `Pillow` first).

---

## 🤝 Contributing

We welcome improvements! Suggested contribution steps:

1. **Fork** the repository & create a feature branch (`git checkout -b feature/your-idea`).
2. **Install dependencies** *(optional GIF export)*:
   ```bash
   pip install pillow
   ```
3. **Keep linting simple** – follow PEP 8 style; no additional tooling required.
4. **Run manual smoke tests** – launch `python main.py`, exercise key paths, export JSON/GIF.
5. **Submit a PR** describing the change, UI impacts, and testing performed.

### Ideas to Explore

- Additional algorithms (e.g., Floyd–Warshall, bidirectional search).
- Save/load custom graphs.
- Theme packs or colorblind-friendly palettes.
- Performance profiling overlays.

---

## 🧭 Repository Guide

```
├── main.py                 # Entry point – launches the Tkinter app
├── dijkstra_game/
│   ├── gui.py              # UI layout, interactions, exports
│   ├── algorithms.py       # Dijkstra, A*, Bellman–Ford explorers
│   ├── graph.py            # Graph structure + manipulation helpers
│   ├── levels.py           # Curated map definitions
│   └── scenarios.py        # Guided scenario presets
├── ALGORITHM.md            # Deep dive into the algorithms & proofs
└── README.md               # You are here
```

---

## 📄 License

This project is released under the MIT License. See `LICENSE` (or the repository page) for details.

---

## 🙋 Support & Feedback

Found a bug? Have an idea? Open an issue or start a discussion on GitHub.  
Enjoy the simulator and happy pathfinding!
