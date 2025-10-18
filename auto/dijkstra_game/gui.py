from __future__ import annotations

import json
import math
import os
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog, ttk
from typing import Dict, List, Optional, Tuple

from .algorithms import (
    AStarExplorer,
    BellmanFordExplorer,
    DijkstraExplorer,
    PathResult,
    PathStep,
)
from .graph import WeightedGraph
from .levels import Level, get_levels
from .scenarios import Scenario, get_scenarios


COLOR_BACKGROUND = "#0b132b"
COLOR_PANEL = "#1c2541"
COLOR_CANVAS = "#0f192a"
COLOR_TEXT_PRIMARY = "#f8f9fa"
COLOR_MUTED = "#94a3b8"
COLOR_DEFAULT_NODE = "#1f6feb"
COLOR_VISITED = "#f97068"
COLOR_FRONTIER = "#9b5de5"
COLOR_CURRENT = "#facc15"
COLOR_START = "#10b981"
COLOR_GOAL = "#ef4444"
COLOR_EDGE = "#233554"
COLOR_EDGE_ACTIVE = "#f59e0b"
COLOR_EDGE_PATH = "#22c55e"
COLOR_EDIT_SELECT = "#2dd4bf"
COLOR_PATH_NODE = "#0ea5e9"

EFFICIENCY_TARGET = 18.0


class Tooltip:
    """Lightweight tooltip helper for Tk widgets."""

    def __init__(self, widget: tk.Widget, text: str) -> None:
        self.widget = widget
        self.text = text
        self.tipwindow: Optional[tk.Toplevel] = None
        widget.bind("<Enter>", self._show)
        widget.bind("<Leave>", self._hide)

    def _show(self, _: tk.Event) -> None:
        if self.tipwindow or not self.text:
            return
        x = self.widget.winfo_rootx() + 20
        y = self.widget.winfo_rooty() + self.widget.winfo_height() + 8
        self.tipwindow = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.configure(background=COLOR_PANEL)
        label = tk.Label(
            tw,
            text=self.text,
            background=COLOR_PANEL,
            foreground=COLOR_TEXT_PRIMARY,
            relief="solid",
            borderwidth=1,
            font=("Helvetica", 9),
            padx=6,
            pady=3,
        )
        label.pack()
        tw.wm_geometry(f"+{x}+{y}")

    def _hide(self, _: tk.Event) -> None:
        if self.tipwindow:
            self.tipwindow.destroy()
            self.tipwindow = None


class SimulatorApp:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("Dijkstra Adventure Simulator")
        self.root.configure(bg=COLOR_BACKGROUND)
        self.root.minsize(980, 700)

        ttk.Style().theme_use("clam")
        style = ttk.Style()
        style.configure("TFrame", background=COLOR_PANEL)
        style.configure("TLabel", background=COLOR_PANEL, foreground=COLOR_TEXT_PRIMARY, font=("Helvetica", 11))
        style.configure("Header.TLabel", font=("Helvetica", 18, "bold"))
        style.configure("TButton", font=("Helvetica", 11), padding=(4, 0), height=1)
        style.configure("Accent.TButton", font=("Helvetica", 11, "bold"), padding=(4, 0), height=1)
        style.configure("Info.TLabel", foreground=COLOR_MUTED, font=("Helvetica", 10))
        style.configure("TCheckbutton", background=COLOR_PANEL, foreground=COLOR_TEXT_PRIMARY)
        style.configure("TRadiobutton", background=COLOR_PANEL, foreground=COLOR_TEXT_PRIMARY)

        self.levels: List[Level] = list(get_levels())
        self.scenarios: List[Scenario] = list(get_scenarios())
        self._scenario_names: List[str] = ["Free Play"] + [scenario.name for scenario in self.scenarios]
        self.level_var = tk.StringVar(value=self.levels[0].name)
        self.selection_mode = tk.StringVar(value="start")
        self.speed_var = tk.DoubleVar(value=550.0)
        self.status_var = tk.StringVar(value="Select a start and goal node, then press Run Simulation.")
        self.current_info_var = tk.StringVar(value="Current: —")
        self.distances_var = tk.StringVar(value="")
        self.path_var = tk.StringVar(value="Path: —")
        self.cost_var = tk.StringVar(value="Cost: —")
        self.algorithm_var = tk.StringVar(value="Dijkstra")
        self.scenario_var = tk.StringVar(value="Free Play")
        self.scenario_info_var = tk.StringVar(value="Scenario: Free Play")
        self.available_algorithms: Dict[str, type] = {
            "Dijkstra": DijkstraExplorer,
            "A*": AStarExplorer,
            "Bellman-Ford": BellmanFordExplorer,
        }
        self.achievements: Dict[str, bool] = {
            "First Run": False,
            "Algorithm Explorer": False,
            "Efficiency Star": False,
        }
        self.algorithms_used: set[str] = set()
        self.achievements_var = tk.StringVar(value="Achievements: [ ] First Run  [ ] Algorithm Explorer  [ ] Efficiency Star")

        self.edit_mode = tk.BooleanVar(value=False)
        self.pending_edit_action: Optional[str] = None
        self.edit_selection: Optional[str] = None
        self.dragging_node: Optional[str] = None
        self.drag_offset: Tuple[float, float] = (0.0, 0.0)
        self.drag_moved = False
        self.highlighted_node: Optional[str] = None
        self.current_scenario: Optional[Scenario] = None
        self.tooltips: List[Tooltip] = []
        self.zoom_factor = 1.0
        self.zoom_var = tk.DoubleVar(value=1.0)
        self.zoom_min = 0.6
        self.zoom_max = 1.6
        self.zoom_step = 0.1
        self.edit_panel: Optional[ttk.LabelFrame] = None
        self.final_path_nodes: set[str] = set()
        self.final_path_edges: set[Tuple[str, str]] = set()
        self.canvas_menu: Optional[tk.Menu] = None
        self.node_menu: Optional[tk.Menu] = None
        self._menu_click_position: Tuple[float, float] | None = None
        self.pending_edge_start: Optional[str] = None
        self.undo_stack: List[Tuple[WeightedGraph, Optional[str], Optional[str], set[str], set[Tuple[str, str]]]] = []
        self.node_radius = 22
        self.canvas_pad_x = 70
        self.canvas_pad_y = 70
        self.custom_node_index = 1

        self.current_level: Level = self.levels[0]
        self.graph: WeightedGraph = self.current_level.build_graph()
        self.start_node: Optional[str] = self.current_level.default_start
        self.goal_node: Optional[str] = self.current_level.default_goal

        self.result: Optional[PathResult] = None
        self.steps: List[PathStep] = []
        self.step_index: int = -1
        self.animation_after: Optional[str] = None
        self.traveler_id: Optional[int] = None

        self.canvas: Optional[tk.Canvas] = None
        self.node_items: Dict[str, Dict[str, int]] = {}
        self.edge_items: Dict[Tuple[str, str], int] = {}
        self.edge_labels: Dict[Tuple[str, str], int] = {}
        self.node_positions: Dict[str, Tuple[float, float]] = {}

        self._build_layout()
        self._draw_graph()
        self._update_achievements_display()
        self._update_status("Ready to explore shortest paths.")

    # --------------------------------------------------------------------- UI
    def _build_layout(self) -> None:
        main = ttk.Frame(self.root)
        main.pack(fill="both", expand=True, padx=18, pady=18)
        main.columnconfigure(0, weight=0)
        main.columnconfigure(1, weight=1)
        main.rowconfigure(0, weight=1)

        control_frame = ttk.Frame(main, padding=16)
        control_frame.grid(row=0, column=0, sticky="ns")
        control_frame.columnconfigure(0, weight=1)

        ttk.Label(control_frame, text="Dijkstra Adventure", style="Header.TLabel").grid(row=0, column=0, sticky="w")
        ttk.Label(control_frame, text="Visualize the journey of a pathfinding drone across stylized maps.",
                  style="Info.TLabel", wraplength=240, justify="left").grid(row=1, column=0, pady=(4, 12), sticky="w")

        ttk.Label(control_frame, text="Level").grid(row=2, column=0, sticky="w")
        level_menu = ttk.Combobox(
            control_frame,
            textvariable=self.level_var,
            values=[level.name for level in self.levels],
            state="readonly",
        )
        level_menu.grid(row=3, column=0, sticky="ew")
        level_menu.bind("<<ComboboxSelected>>", self._on_level_changed)
        self._add_tooltip(level_menu, "Choose the active map layout.")

        ttk.Label(control_frame, text="Scenario").grid(row=4, column=0, sticky="w", pady=(8, 0))
        scenario_combo = ttk.Combobox(
            control_frame,
            textvariable=self.scenario_var,
            values=self._scenario_names,
            state="readonly",
        )
        scenario_combo.grid(row=5, column=0, sticky="ew")
        scenario_combo.bind("<<ComboboxSelected>>", self._on_scenario_selected)
        self._add_tooltip(scenario_combo, "Pick a guided mission, then click Apply to configure the map.")
        apply_scenario_btn = ttk.Button(control_frame, text="Apply Scenario", command=self.apply_scenario)
        apply_scenario_btn.grid(row=6, column=0, sticky="ew", pady=(4, 0))
        self._add_tooltip(apply_scenario_btn, "Load the scenario's level, start/goal nodes, and recommended algorithm.")
        ttk.Label(control_frame, textvariable=self.scenario_info_var, style="Info.TLabel", wraplength=240, justify="left").grid(
            row=7, column=0, sticky="w", pady=(4, 12)
        )

        ttk.Separator(control_frame).grid(row=8, column=0, pady=12, sticky="ew")

        ttk.Label(control_frame, text="Node Selection").grid(row=9, column=0, sticky="w")

        radio_frame = ttk.Frame(control_frame)
        radio_frame.grid(row=10, column=0, sticky="ew", pady=(4, 8))
        ttk.Radiobutton(radio_frame, text="Pick Start", value="start", variable=self.selection_mode).grid(row=0, column=0, sticky="w")
        ttk.Radiobutton(radio_frame, text="Pick Goal", value="goal", variable=self.selection_mode).grid(row=0, column=1, sticky="w", padx=(12, 0))

        self.start_label = ttk.Label(control_frame, text=self._format_node_label("Start", self.start_node))
        self.start_label.grid(row=11, column=0, sticky="w", pady=(0, 4))
        self.goal_label = ttk.Label(control_frame, text=self._format_node_label("Goal", self.goal_node))
        self.goal_label.grid(row=12, column=0, sticky="w")

        ttk.Label(control_frame, text="Algorithm").grid(row=13, column=0, sticky="w", pady=(8, 0))
        algorithm_combo = ttk.Combobox(
            control_frame,
            textvariable=self.algorithm_var,
            values=list(self.available_algorithms.keys()),
            state="readonly",
        )
        algorithm_combo.grid(row=14, column=0, sticky="ew")
        algorithm_combo.bind("<<ComboboxSelected>>", self._on_algorithm_changed)
        self._add_tooltip(algorithm_combo, "Select the pathfinding strategy to visualize.")

        button_frame = ttk.Frame(control_frame)
        button_frame.grid(row=15, column=0, pady=12, sticky="ew")
        button_frame.columnconfigure(0, weight=1)
        button_frame.columnconfigure(1, weight=1)

        run_btn = ttk.Button(button_frame, text="Run Simulation", style="Accent.TButton", command=self.run_simulation)
        run_btn.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 8))
        self._add_tooltip(run_btn, "Play the selected algorithm from start to finish.")

        step_btn = ttk.Button(button_frame, text="Step", command=self.step_simulation)
        step_btn.grid(row=1, column=0, sticky="ew", padx=(0, 4))
        self._add_tooltip(step_btn, "Advance the visualization one snapshot at a time.")
        reset_btn = ttk.Button(button_frame, text="Reset", command=self.reset_simulation)
        reset_btn.grid(row=1, column=1, sticky="ew", padx=(4, 0))
        self._add_tooltip(reset_btn, "Clear the current run and prepare for another attempt.")

        random_btn = ttk.Button(button_frame, text="Randomize Weights", command=self.randomize_weights)
        random_btn.grid(row=2, column=0, columnspan=2, sticky="ew", pady=(8, 0))
        self._add_tooltip(random_btn, "Assign fresh weights to every edge on the graph.")
        swap_btn = ttk.Button(button_frame, text="Swap Start/Goal", command=self.swap_nodes)
        swap_btn.grid(row=3, column=0, columnspan=2, sticky="ew", pady=(6, 0))
        self._add_tooltip(swap_btn, "Invert the start and goal nodes without changing anything else.")
        compare_btn = ttk.Button(button_frame, text="Compare Algorithms", command=self.compare_algorithms)
        compare_btn.grid(row=4, column=0, columnspan=2, sticky="ew", pady=(8, 0))
        self._add_tooltip(compare_btn, "Run all algorithms and compare their costs and step counts.")
        export_json_btn = ttk.Button(button_frame, text="Export JSON", command=self.export_json)
        export_json_btn.grid(row=5, column=0, sticky="ew", padx=(0, 4), pady=(8, 0))
        self._add_tooltip(export_json_btn, "Save the detailed run history as a JSON log.")
        export_gif_btn = ttk.Button(button_frame, text="Export GIF", command=self.export_gif)
        export_gif_btn.grid(row=5, column=1, sticky="ew", padx=(4, 0), pady=(8, 0))
        self._add_tooltip(export_gif_btn, "Render the animation as an animated GIF (requires Pillow).")

        ttk.Separator(control_frame).grid(row=16, column=0, pady=12, sticky="ew")

        ttk.Label(control_frame, text="Animation Speed").grid(row=17, column=0, sticky="w")
        speed_scale = ttk.Scale(control_frame, from_=150, to=1000, variable=self.speed_var, command=self._on_speed_changed)
        speed_scale.grid(row=18, column=0, sticky="ew")
        ttk.Label(control_frame, text="Lower is faster.", style="Info.TLabel").grid(row=19, column=0, sticky="w", pady=(4, 8))

        ttk.Label(control_frame, textvariable=self.status_var, wraplength=260, style="Info.TLabel", justify="left").grid(
            row=20, column=0, sticky="w", pady=(8, 12)
        )

        ttk.Label(control_frame, textvariable=self.current_info_var).grid(row=21, column=0, sticky="w")
        ttk.Label(control_frame, textvariable=self.cost_var).grid(row=22, column=0, sticky="w", pady=(4, 0))
        ttk.Label(control_frame, textvariable=self.path_var, wraplength=240, justify="left").grid(row=23, column=0, sticky="w", pady=(2, 0))
        ttk.Label(control_frame, textvariable=self.distances_var, style="Info.TLabel", wraplength=240, justify="left").grid(
            row=24, column=0, sticky="w", pady=(8, 0)
        )

        ttk.Label(control_frame, textvariable=self.achievements_var, style="Info.TLabel", wraplength=240, justify="left").grid(
            row=25, column=0, sticky="w", pady=(8, 0)
        )

        canvas_frame = ttk.Frame(main, padding=12)
        canvas_frame.grid(row=0, column=1, sticky="nsew")
        canvas_frame.columnconfigure(0, weight=1)
        canvas_frame.rowconfigure(0, weight=1)

        self.canvas = tk.Canvas(
            canvas_frame,
            background=COLOR_CANVAS,
            highlightthickness=0,
            width=720,
            height=620,
        )
        self.canvas.grid(row=0, column=0, sticky="nsew")
        self.canvas.bind("<Configure>", self._on_canvas_resized)
        self.canvas.bind("<Button-1>", self._on_canvas_primary_click)
        self.canvas.bind("<Double-Button-1>", self._on_canvas_double_click)
        self.canvas.bind("<MouseWheel>", self._on_canvas_wheel)
        self.canvas.bind("<Button-4>", self._on_canvas_wheel)
        self.canvas.bind("<Button-5>", self._on_canvas_wheel)
        self.canvas.bind("<Button-3>", self._on_canvas_right_click)
        self.canvas.bind("<Button-2>", self._on_canvas_right_click)
        self.root.bind_all("<Control-z>", self._on_undo)
        self.root.bind_all("<Command-z>", self._on_undo)

        self._build_edit_panel(canvas_frame)
        self._create_menus()

    def _build_edit_panel(self, parent: ttk.Frame) -> None:
        panel = ttk.LabelFrame(parent, text="Graph Editing", padding=8)
        panel.place(relx=1.0, rely=0.0, anchor="ne", x=-12, y=12)
        panel.columnconfigure(0, weight=1)
        panel.columnconfigure(1, weight=1)

        edit_check = ttk.Checkbutton(
            panel,
            text="Enable Edit Mode",
            variable=self.edit_mode,
            command=self._on_edit_mode_toggled,
        )
        edit_check.grid(row=0, column=0, columnspan=2, sticky="w")
        self._add_tooltip(edit_check, "Toggle interactive graph editing (drag, add, remove nodes and edges).")

        ttk.Label(panel, text="Actions").grid(row=1, column=0, columnspan=2, sticky="w", pady=(6, 2))
        action_buttons = [
            ("Add Node", "add_node", "Click the canvas to place a new node."),
            ("Remove Node", "remove_node", "Select an existing node to delete it and its edges."),
            ("Add Edge", "add_edge", "Choose two nodes to connect them with a weighted edge."),
            ("Remove Edge", "remove_edge", "Select two connected nodes to remove their edge."),
            ("Set Weight", "set_weight", "Pick an edge's endpoints to update its weight."),
        ]

        for idx, (label, action, tip) in enumerate(action_buttons, start=0):
            row = 2 + idx // 2
            col = idx % 2
            btn = ttk.Button(panel, text=label, command=lambda a=action: self._set_edit_action(a))
            btn.grid(row=row, column=col, sticky="ew", padx=(0 if col == 0 else 4, 4 if col == 0 else 0), pady=(0, 4))
            self._add_tooltip(btn, tip)

        clear_row = 5
        clear_btn = ttk.Button(panel, text="Clear Action", command=lambda: self._set_edit_action(None))
        clear_btn.grid(row=clear_row, column=0, columnspan=2, sticky="ew", pady=(0, 6))
        self._add_tooltip(clear_btn, "Return to neutral state while keeping edit mode on.")

        ttk.Separator(panel).grid(row=clear_row + 1, column=0, columnspan=2, sticky="ew", pady=6)
        ttk.Label(panel, text="Zoom").grid(row=clear_row + 2, column=0, columnspan=2, sticky="w")
        zoom_scale = ttk.Scale(
            panel,
            from_=0.6,
            to=1.6,
            variable=self.zoom_var,
            command=self._on_zoom_slider,
        )
        zoom_scale.grid(row=clear_row + 3, column=0, columnspan=2, sticky="ew")
        self._add_tooltip(zoom_scale, "Adjust the canvas zoom level.")

        zoom_out_btn = ttk.Button(panel, text="−", width=3, command=self._zoom_out)
        zoom_out_btn.grid(row=clear_row + 4, column=0, sticky="ew", pady=(6, 0), padx=(0, 4))
        self._add_tooltip(zoom_out_btn, "Zoom out a step.")
        zoom_in_btn = ttk.Button(panel, text="+", width=3, command=self._zoom_in)
        zoom_in_btn.grid(row=clear_row + 4, column=1, sticky="ew", pady=(6, 0))
        self._add_tooltip(zoom_in_btn, "Zoom in a step.")

        self.edit_panel = panel

    def _create_menus(self) -> None:
        self.canvas_menu = tk.Menu(self.root, tearoff=0)
        self.canvas_menu.add_command(label="Add Node…", command=self._menu_add_node_here)
        self.canvas_menu.add_separator()
        self.canvas_menu.add_command(label="Clear Graph", command=self._menu_clear_graph)
        self.canvas_menu.add_separator()
        self.canvas_menu.add_command(label="Reset View", command=lambda: self._apply_zoom(1.0))

        self.node_menu = tk.Menu(self.root, tearoff=0)

    def _menu_add_node_here(self) -> None:
        if not self.canvas or not self._menu_click_position:
            return
        x, y = self._menu_click_position
        self._prompt_add_node_at(x, y)

    def _menu_clear_graph(self) -> None:
        self.graph = WeightedGraph({}, [])
        self.start_node = None
        self.goal_node = None
        self.custom_node_index = 1
        self.start_label.config(text=self._format_node_label("Start", self.start_node))
        self.goal_label.config(text=self._format_node_label("Goal", self.goal_node))
        self.pending_edge_start = None
        self._clear_final_highlight(refresh=False)
        self.reset_simulation(redraw=True)
        self._update_status("Cleared graph. Right-click to add new nodes.")

    def _populate_node_menu(self, node_id: str) -> None:
        if not self.node_menu:
            return
        self.node_menu.delete(0, tk.END)
        self.node_menu.add_command(label="Set as Start", command=lambda: self._menu_set_start(node_id))
        self.node_menu.add_command(label="Set as Goal", command=lambda: self._menu_set_goal(node_id))
        self.node_menu.add_separator()

        if self.pending_edge_start and self.pending_edge_start != node_id:
            label = f"Complete edge from {self.pending_edge_start}"
            self.node_menu.add_command(label=label, command=lambda: self._menu_finish_edge(self.pending_edge_start, node_id))
            self.node_menu.add_command(label="Cancel edge placement", command=self._menu_cancel_edge)
        else:
            self.node_menu.add_command(label="Begin edge here", command=lambda: self._menu_start_edge(node_id))

        neighbors = sorted(self.graph.neighbors(node_id))
        if neighbors:
            self.node_menu.add_separator()
            self.node_menu.add_command(label="Remove edge…", command=lambda: self._menu_remove_edge(node_id))
            self.node_menu.add_command(label="Set edge weight…", command=lambda: self._menu_set_edge_weight(node_id))

        self.node_menu.add_separator()
        self.node_menu.add_command(label="Remove node", command=lambda: self._menu_remove_node(node_id))
        self.node_menu.add_command(label="Rename node…", command=lambda: self._menu_rename_node(node_id))

    def _menu_set_start(self, node_id: str) -> None:
        self.start_node = node_id
        self.start_label.config(text=self._format_node_label("Start", self.start_node))
        self.pending_edge_start = None
        self.reset_simulation()
        self._update_status(f"Start node set to {self._node_name(node_id)}.")

    def _menu_set_goal(self, node_id: str) -> None:
        self.goal_node = node_id
        self.goal_label.config(text=self._format_node_label("Goal", self.goal_node))
        self.pending_edge_start = None
        self.reset_simulation()
        self._update_status(f"Goal node set to {self._node_name(node_id)}.")

    def _menu_remove_node(self, node_id: str) -> None:
        try:
            self._push_undo()
            self.graph.remove_node(node_id)
        except ValueError as exc:
            messagebox.showerror("Remove Node", str(exc), parent=self.root)
            return
        if self.pending_edge_start == node_id:
            self.pending_edge_start = None
        if self.start_node == node_id:
            self.start_node = None
            self.start_label.config(text=self._format_node_label("Start", self.start_node))
        if self.goal_node == node_id:
            self.goal_node = None
            self.goal_label.config(text=self._format_node_label("Goal", self.goal_node))
        self._clear_final_highlight(refresh=False)
        self.reset_simulation(redraw=True)
        self._update_status(f"Removed node {node_id}.")

    def _menu_rename_node(self, node_id: str) -> None:
        current = self.graph.nodes[node_id].label
        label_text = simpledialog.askstring(
            "Rename Node",
            f"Enter new label for node {node_id}:",
            initialvalue=current,
            parent=self.root,
        )
        if label_text is None:
            return
        label = label_text.strip() or current
        try:
            self._push_undo()
            self.graph.update_node_label(node_id, label)
        except ValueError as exc:
            messagebox.showerror("Rename Node", str(exc), parent=self.root)
            return
        self.reset_simulation(redraw=True)
        self._update_status(f"Renamed node {node_id} to {label}.")

    def _menu_start_edge(self, node_id: str) -> None:
        self.pending_edge_start = node_id
        self._update_status(f"Select another node to connect with {node_id}.")

    def _menu_cancel_edge(self) -> None:
        self.pending_edge_start = None
        self._update_status("Edge placement canceled.")

    def _menu_finish_edge(self, start: str, end: str) -> None:
        if start == end:
            self._update_status("Cannot create edge from a node to itself.")
            return
        weight = simpledialog.askfloat(
            "Edge Weight",
            f"Weight for edge {start}–{end}:",
            minvalue=0.1,
            parent=self.root,
        )
        if weight is None:
            self._update_status("Edge creation canceled.")
            return
        try:
            self._push_undo()
            self.graph.add_edge(start, end, weight)
        except ValueError as exc:
            messagebox.showerror("Add Edge", str(exc), parent=self.root)
            return
        self.pending_edge_start = None
        self._clear_final_highlight(refresh=False)
        self.reset_simulation(redraw=True)
        self._update_status(f"Added edge {start}–{end} with weight {self._format_weight(weight)}.")

    def _menu_remove_edge(self, node_id: str) -> None:
        neighbor = self._choose_neighbor(node_id, "Remove edge to which neighbor?")
        if neighbor is None:
            return
        try:
            self._push_undo()
            self.graph.remove_edge(node_id, neighbor)
        except ValueError as exc:
            messagebox.showerror("Remove Edge", str(exc), parent=self.root)
            return
        self._clear_final_highlight(refresh=False)
        self.reset_simulation(redraw=True)
        self._update_status(f"Removed edge {node_id}–{neighbor}.")

    def _menu_set_edge_weight(self, node_id: str) -> None:
        neighbor = self._choose_neighbor(node_id, "Update weight to which neighbor?")
        if neighbor is None:
            return
        current = self.graph.edge_weight(node_id, neighbor)
        new_weight = simpledialog.askfloat(
            "Edge Weight",
            f"Enter new weight for edge {node_id}–{neighbor}:",
            initialvalue=current,
            minvalue=0.1,
            parent=self.root,
        )
        if new_weight is None:
            return
        try:
            self._push_undo()
            self.graph.set_edge_weight(node_id, neighbor, new_weight)
        except KeyError:
            messagebox.showerror("Set Weight", "Edge no longer exists.", parent=self.root)
            return
        self._clear_final_highlight(refresh=False)
        self.reset_simulation(redraw=True)
        self._update_status(f"Updated edge {node_id}–{neighbor} to {self._format_weight(new_weight)}.")

    def _choose_neighbor(self, node_id: str, prompt: str) -> Optional[str]:
        neighbors = sorted(self.graph.neighbors(node_id))
        if not neighbors:
            messagebox.showinfo("No Neighbors", f"Node {node_id} has no connected edges.", parent=self.root)
            return None
        choice = simpledialog.askinteger(
            "Select Neighbor",
            f"{prompt}\nChoose index: {', '.join(f'[{i+1}] {n}' for i, n in enumerate(neighbors))}",
            minvalue=1,
            maxvalue=len(neighbors),
            parent=self.root,
        )
        if choice is None:
            return None
        return neighbors[choice - 1]


    def _on_zoom_slider(self, _: str) -> None:
        self._apply_zoom(self.zoom_var.get(), announce=False)

    def _zoom_in(self) -> None:
        self._apply_zoom(self.zoom_factor + self.zoom_step)

    def _zoom_out(self) -> None:
        self._apply_zoom(self.zoom_factor - self.zoom_step)

    def _on_canvas_wheel(self, event: tk.Event) -> None:
        delta = 0
        if getattr(event, "delta", 0):
            delta = event.delta
        elif getattr(event, "num", None) == 4:
            delta = 120
        elif getattr(event, "num", None) == 5:
            delta = -120
        if delta == 0:
            return
        step = self.zoom_step * (1.0 if delta > 0 else -1.0)
        self._apply_zoom(self.zoom_factor + step, announce=False)

    def _apply_zoom(self, value: float, announce: bool = True) -> None:
        clamped = min(self.zoom_max, max(self.zoom_min, value))
        if abs(clamped - self.zoom_factor) < 1e-3 and abs(self.zoom_var.get() - clamped) < 1e-3:
            return
        self.zoom_factor = clamped
        if abs(self.zoom_var.get() - clamped) > 1e-3:
            self.zoom_var.set(clamped)
        self._draw_graph()
        if announce:
            self._update_status(f"Zoom set to {clamped:.2f}×")

    # ------------------------------------------------------------------ Control
    def _on_level_changed(self, _: tk.Event | None = None) -> None:
        name = self.level_var.get()
        for level in self.levels:
            if level.name == name:
                self.current_level = level
                break
        self.graph = self.current_level.build_graph()
        self.custom_node_index = 1
        self.start_node = self.current_level.default_start
        self.goal_node = self.current_level.default_goal
        self.selection_mode.set("start")
        self.edit_selection = None
        self._clear_highlight()
        self.undo_stack.clear()
        self.reset_simulation(redraw=True)
        description = f"{self.current_level.description}\nStart: {self._node_name(self.start_node)} • Goal: {self._node_name(self.goal_node)}"
        self._update_status(description)

    def _find_scenario(self, name: str) -> Optional[Scenario]:
        for scenario in self.scenarios:
            if scenario.name == name:
                return scenario
        return None

    def _on_scenario_selected(self, _: tk.Event | None = None) -> None:
        scenario = self._find_scenario(self.scenario_var.get())
        if scenario:
            self.scenario_info_var.set(f"Scenario: {scenario.name} – {scenario.description}")
        else:
            self.current_scenario = None
            self.scenario_info_var.set("Scenario: Free Play")

    def apply_scenario(self) -> None:
        scenario = self._find_scenario(self.scenario_var.get())
        if not scenario:
            self.current_scenario = None
            self.scenario_info_var.set("Scenario: Free Play")
            self._update_status("Free play mode. Configure any nodes and algorithms you like.")
            return

        self.current_scenario = scenario
        if scenario.level_name != self.current_level.name:
            self.level_var.set(scenario.level_name)
            self._on_level_changed()

        if scenario.start not in self.graph.nodes or scenario.goal not in self.graph.nodes:
            self._update_status("Scenario nodes are not available on this level configuration.")
            return

        self.start_node = scenario.start
        self.goal_node = scenario.goal
        self.selection_mode.set("start")
        self.start_label.config(text=self._format_node_label("Start", self.start_node))
        self.goal_label.config(text=self._format_node_label("Goal", self.goal_node))

        algorithm_changed = False
        if scenario.algorithm and scenario.algorithm in self.available_algorithms:
            if self.algorithm_var.get() != scenario.algorithm:
                self.algorithm_var.set(scenario.algorithm)
                algorithm_changed = True

        self.edit_selection = None
        self._clear_highlight()
        if algorithm_changed:
            self._on_algorithm_changed()
        else:
            self.reset_simulation()
        self.scenario_info_var.set(f"Scenario: {scenario.name} – {scenario.description}")
        self._update_status(f"Loaded scenario '{scenario.name}'. {scenario.description}")

    def _on_speed_changed(self, _: str) -> None:
        # UI callback required even if body is empty; we update delay lazily via property.
        pass

    def _on_algorithm_changed(self, _: tk.Event | None = None) -> None:
        self.reset_simulation()
        self._update_status(f"{self.algorithm_var.get()} selected. Ready to explore.")

    def run_simulation(self) -> None:
        if not self._prepare_steps():
            return
        self._cancel_animation()
        self.step_index = -1
        self._animate_next_step()

    def step_simulation(self) -> None:
        if not self._prepare_steps():
            return
        self._cancel_animation()
        if self.step_index + 1 < len(self.steps):
            self.step_index += 1
            step = self.steps[self.step_index]
            self._apply_step(step)
            if self.step_index == len(self.steps) - 1:
                self._on_simulation_complete()
        else:
            self._update_status("Simulation already complete. Reset or randomize to explore again.")

    def reset_simulation(self, redraw: bool = False) -> None:
        self._cancel_animation()
        self.result = None
        self.steps = []
        self.step_index = -1
        self.current_info_var.set("Current: —")
        self.path_var.set("Path: —")
        self.cost_var.set("Cost: —")
        self.distances_var.set("")
        self.status_var.set("Simulation reset.")
        self._clear_final_highlight(refresh=True)
        if redraw:
            self._draw_graph()
        else:
            self._refresh_node_styles()
        self._remove_traveler()

    def randomize_weights(self) -> None:
        self.graph.randomize_weights()
        for (source, target), label_id in self.edge_labels.items():
            weight = self.graph.edge_weight(source, target)
            self.canvas.itemconfigure(label_id, text=self._format_weight(weight))
        self.reset_simulation()
        self._update_status("Weights randomized. Run the simulation to watch a new route.")

    def swap_nodes(self) -> None:
        if self.start_node and self.goal_node:
            self.start_node, self.goal_node = self.goal_node, self.start_node
            self.start_label.config(text=self._format_node_label("Start", self.start_node))
            self.goal_label.config(text=self._format_node_label("Goal", self.goal_node))
            self.reset_simulation()
            self._update_status("Swapped start and goal nodes.")

    # ------------------------------------------------------------- Drawing logic
    def _current_radius(self) -> float:
        base = self.node_radius * self.zoom_factor
        return max(14.0, min(48.0, base))

    def _edge_width(self) -> int:
        return max(2, int(round(3 * self.zoom_factor)))

    def _highlight_edge_width(self) -> int:
        return self._edge_width() + 2

    def _node_outline_width(self) -> int:
        return max(2, int(round(2 * self.zoom_factor)))

    def _draw_graph(self) -> None:
        if not self.canvas:
            return
        self.canvas.delete("all")
        self.node_items.clear()
        self.edge_items.clear()
        self.edge_labels.clear()
        self.node_positions.clear()
        width = self.canvas.winfo_width() or 720
        height = self.canvas.winfo_height() or 620
        radius = self._current_radius()
        outline_width = self._node_outline_width()
        edge_width = self._edge_width()

        for source, target, weight in self.graph.edges():
            x1, y1 = self._project(self.graph.nodes[source].position, width, height)
            x2, y2 = self._project(self.graph.nodes[target].position, width, height)
            line_id = self.canvas.create_line(
                x1,
                y1,
                x2,
                y2,
                width=edge_width,
                fill=COLOR_EDGE,
            )
            label_x = (x1 + x2) / 2
            label_y = (y1 + y2) / 2
            label_id = self.canvas.create_text(
                label_x,
                label_y,
                text=self._format_weight(weight),
                fill=COLOR_MUTED,
                font=("Helvetica", 11, "bold"),
                justify="center",
                tags=("weight",),
            )
            key = self._edge_key(source, target)
            self.edge_items[key] = line_id
            self.edge_labels[key] = label_id

        for node_id, info in self.graph.nodes.items():
            cx, cy = self._project(info.position, width, height)
            self.node_positions[node_id] = (cx, cy)

            oval_id = self.canvas.create_oval(
                cx - radius,
                cy - radius,
                cx + radius,
                cy + radius,
                fill=COLOR_DEFAULT_NODE,
                outline="#0a1121",
                width=outline_width,
                tags=("node", node_id),
            )
            label_id = self.canvas.create_text(
                cx,
                cy,
                text=node_id,
                fill=COLOR_TEXT_PRIMARY,
                font=("Helvetica", 13, "bold"),
            )
            name_id = self.canvas.create_text(
                cx,
                cy + radius + 14,
                text=info.label,
                fill=COLOR_MUTED,
                font=("Helvetica", 9),
            )
            self.node_items[node_id] = {"oval": oval_id, "label": label_id, "name": name_id}

            for tag in (oval_id, label_id, name_id):
                self.canvas.tag_bind(tag, "<ButtonPress-1>", lambda event, nid=node_id: self._on_node_press(event, nid))
                self.canvas.tag_bind(tag, "<B1-Motion>", lambda event, nid=node_id: self._on_node_drag(event, nid))
                self.canvas.tag_bind(tag, "<ButtonRelease-1>", lambda event, nid=node_id: self._on_node_release(nid))
                self.canvas.tag_bind(tag, "<Button-3>", lambda event, nid=node_id: self._on_node_right_click(event, nid))
                self.canvas.tag_bind(tag, "<Button-2>", lambda event, nid=node_id: self._on_node_right_click(event, nid))

        self._refresh_node_styles()
        if self.edit_selection:
            self._highlight_edit_node(self.edit_selection)
        self.traveler_id = None

    def _on_canvas_resized(self, _: tk.Event) -> None:
        self._draw_graph()

    def _refresh_node_styles(self) -> None:
        if not self.canvas:
            return
        edge_width = self._edge_width()
        outline_width = self._node_outline_width()
        for key, line_id in self.edge_items.items():
            self.canvas.itemconfigure(line_id, fill=COLOR_EDGE, width=edge_width)
        for node_id, items in self.node_items.items():
            fill = COLOR_DEFAULT_NODE
            if node_id == self.start_node:
                fill = COLOR_START
            elif node_id == self.goal_node:
                fill = COLOR_GOAL
            self.canvas.itemconfigure(items["oval"], fill=fill, outline="#0a1121", width=outline_width)
        if self.highlighted_node and self.highlighted_node in self.node_items:
            self.canvas.itemconfigure(
                self.node_items[self.highlighted_node]["oval"], outline=COLOR_EDIT_SELECT, width=max(outline_width + 1, 4)
            )
        self.canvas.tag_raise("weight")
        if self.final_path_edges:
            self._apply_final_highlight()

    def _on_edit_mode_toggled(self) -> None:
        if not self.edit_mode.get():
            self.pending_edit_action = None
            self.edit_selection = None
            self._clear_highlight()
            self._update_status("Edit mode disabled. Simulation controls restored.")
        else:
            self._update_status("Edit mode enabled. Choose an editing action, then interact with the canvas.")

    def _set_edit_action(self, action: Optional[str]) -> None:
        if action is not None and not self.edit_mode.get():
            self.edit_mode.set(True)
            self._on_edit_mode_toggled()
        self.pending_edit_action = action
        self.edit_selection = None
        self._clear_highlight()
        if action is None:
            self._update_status("Editing action cleared.")
        elif action == "add_node":
            self._update_status("Add Node: click the canvas background to place the new node.")
        elif action == "remove_node":
            self._update_status("Remove Node: click a node to delete it (edges will also be removed).")
        elif action == "add_edge":
            self._update_status("Add Edge: click two nodes in sequence to connect them.")
        elif action == "remove_edge":
            self._update_status("Remove Edge: click two connected nodes to delete the edge between them.")
        elif action == "set_weight":
            self._update_status("Set Weight: click the two nodes of an existing edge to change its weight.")

    def _on_canvas_primary_click(self, event: tk.Event) -> None:
        if not self.edit_mode.get() or self.pending_edit_action != "add_node" or not self.canvas:
            return
        overlapping = self.canvas.find_overlapping(event.x, event.y, event.x, event.y)
        if overlapping and any("node" in self.canvas.gettags(item) for item in overlapping):
            return
        self._prompt_add_node_at(event.x, event.y)

    def _on_canvas_double_click(self, event: tk.Event) -> None:
        self._prompt_add_node_at(event.x, event.y)

    def _on_canvas_right_click(self, event: tk.Event) -> None:
        if not self.canvas_menu:
            return
        self.canvas.focus_set()
        self._menu_click_position = (event.x, event.y)
        try:
            self.canvas_menu.tk_popup(event.x_root, event.y_root)
        finally:
            self.canvas_menu.grab_release()

    def _prompt_add_node_at(self, x: float, y: float) -> None:
        if not self.canvas:
            return
        width = self.canvas.winfo_width() or 720
        height = self.canvas.winfo_height() or 620
        norm_x, norm_y = self._normalize(x, y, width, height)
        node_id = self._generate_node_id()
        default_label = f"Custom {node_id}"
        label_text = simpledialog.askstring(
            "Add Node",
            "Enter a descriptive label for the new node:",
            initialvalue=default_label,
            parent=self.root,
        )
        if label_text is None:
            self._update_status("Add node canceled.")
            return
        label = label_text.strip() or default_label
        try:
            self.graph.add_node(node_id, label, (norm_x, norm_y))
        except ValueError as exc:
            messagebox.showerror("Add Node", str(exc), parent=self.root)
            return
        self._clear_final_highlight(refresh=False)
        self.reset_simulation(redraw=True)
        self._update_status(f"Added node {node_id}. Drag to reposition or right-click for more options.")
        self._menu_click_position = None

    def _create_custom_node(self, x: float, y: float) -> None:
        self._prompt_add_node_at(x, y)

    def _generate_node_id(self) -> str:
        # Basic counter-based ID generator that avoids collisions with existing nodes.
        while True:
            candidate = f"N{self.custom_node_index}"
            self.custom_node_index += 1
            if candidate not in self.graph.nodes:
                return candidate

    def _on_node_press(self, event: tk.Event, node_id: str) -> None:
        if self.edit_mode.get() and self.pending_edit_action:
            self._handle_node_edit_click(node_id)
            self.dragging_node = None
            self.drag_moved = False
            return
        self.dragging_node = node_id
        self.drag_offset = (
            self.node_positions[node_id][0] - event.x,
            self.node_positions[node_id][1] - event.y,
        )
        self.drag_moved = False

    def _on_node_drag(self, event: tk.Event, node_id: str) -> None:
        if self.pending_edit_action or self.dragging_node != node_id:
            return
        self.drag_moved = True
        new_x = event.x + self.drag_offset[0]
        new_y = event.y + self.drag_offset[1]
        self._move_node_visual(node_id, new_x, new_y)

    def _on_node_release(self, node_id: str) -> None:
        if self.pending_edit_action:
            return
        if self.dragging_node == node_id and self.drag_moved:
            self._finalize_node_drag(node_id)
        else:
            self._on_node_clicked(node_id)
        self.dragging_node = None
        self.drag_moved = False

    def _on_node_right_click(self, event: tk.Event, node_id: str) -> None:
        if not self.node_menu:
            return
        self.canvas.focus_set()
        self._populate_node_menu(node_id)
        try:
            self.node_menu.tk_popup(event.x_root, event.y_root)
        finally:
            self.node_menu.grab_release()

    def _move_node_visual(self, node_id: str, x: float, y: float) -> None:
        if not self.canvas or node_id not in self.node_items:
            return
        width = self.canvas.winfo_width() or 720
        height = self.canvas.winfo_height() or 620
        radius = self._current_radius()
        min_x = self.canvas_pad_x + radius
        max_x = max(min_x, width - self.canvas_pad_x - radius)
        min_y = self.canvas_pad_y + radius
        max_y = max(min_y, height - self.canvas_pad_y - radius)
        cx = min(max(x, min_x), max_x)
        cy = min(max(y, min_y), max_y)
        self.node_positions[node_id] = (cx, cy)
        items = self.node_items[node_id]
        radius = self._current_radius()
        outline_width = self._node_outline_width()
        self.canvas.coords(items["oval"], cx - radius, cy - radius, cx + radius, cy + radius)
        self.canvas.itemconfigure(items["oval"], width=outline_width)
        self.canvas.coords(items["label"], cx, cy)
        self.canvas.coords(items["name"], cx, cy + radius + 14)
        self._update_edges_for_node(node_id)
        if self.highlighted_node == node_id:
            self.canvas.itemconfigure(items["oval"], outline=COLOR_EDIT_SELECT, width=max(outline_width + 1, 4))
        if self.final_path_edges:
            self._apply_final_highlight()

    def _update_edges_for_node(self, node_id: str) -> None:
        if not self.canvas:
            return
        cx, cy = self.node_positions.get(node_id, (None, None))
        if cx is None:
            return
        for neighbor_id in self.graph.neighbors(node_id):
            key = self._edge_key(node_id, neighbor_id)
            line_id = self.edge_items.get(key)
            neighbor_pos = self.node_positions.get(neighbor_id)
            if not line_id or not neighbor_pos:
                continue
            nx, ny = neighbor_pos
            self.canvas.coords(line_id, cx, cy, nx, ny)
            self.canvas.itemconfigure(line_id, width=self._edge_width())
            label_id = self.edge_labels.get(key)
            if label_id:
                self.canvas.coords(label_id, (cx + nx) / 2, (cy + ny) / 2)
        if self.final_path_edges:
            self._apply_final_highlight_edges_only()

    def _finalize_node_drag(self, node_id: str) -> None:
        if not self.canvas:
            return
        width = self.canvas.winfo_width() or 720
        height = self.canvas.winfo_height() or 620
        cx, cy = self.node_positions.get(node_id, (None, None))
        if cx is None:
            return
        norm_x, norm_y = self._normalize(cx, cy, width, height)
        try:
            self.graph.update_node_position(node_id, (norm_x, norm_y))
        except ValueError:
            return
        self.reset_simulation()
        self._update_status(f"Moved node {node_id} to a new position.")

    def _handle_node_edit_click(self, node_id: str) -> None:
        if not self.pending_edit_action:
            return
        if self.pending_edit_action == "remove_node":
            confirm = messagebox.askyesno(
                "Remove Node",
                f"Delete node {node_id}? All connected edges will also be removed.",
                parent=self.root,
            )
            if not confirm:
                return
            try:
                self.graph.remove_node(node_id)
            except ValueError as exc:
                messagebox.showerror("Remove Node", str(exc), parent=self.root)
                return
            if self.start_node == node_id:
                self.start_node = None
                self.start_label.config(text=self._format_node_label("Start", self.start_node))
            if self.goal_node == node_id:
                self.goal_node = None
                self.goal_label.config(text=self._format_node_label("Goal", self.goal_node))
            self.reset_simulation(redraw=True)
            self._update_status(f"Removed node {node_id}. Select another target or clear the action.")
            return

        if self.pending_edit_action in {"add_edge", "remove_edge", "set_weight"}:
            self._handle_edge_selection(node_id)

    def _handle_edge_selection(self, node_id: str) -> None:
        action = self.pending_edit_action
        if not action:
            return
        if self.edit_selection is None:
            self.edit_selection = node_id
            self._highlight_edit_node(node_id)
            if action == "add_edge":
                self._update_status(f"Selected {node_id}. Click another node to connect.")
            elif action == "remove_edge":
                self._update_status(f"Selected {node_id}. Choose the connected node to remove the edge.")
            else:
                self._update_status(f"Selected {node_id}. Choose the other endpoint to adjust the weight.")
            return

        first = self.edit_selection
        if node_id == first:
            self._update_status("Select a different node to complete the action.")
            return

        if action == "add_edge":
            if node_id in self.graph.neighbors(first):
                self._update_status(f"Edge {first}–{node_id} already exists. Choose another pair or adjust the weight.")
                return
        elif action in {"remove_edge", "set_weight"}:
            if node_id not in self.graph.neighbors(first):
                messagebox.showerror(
                    "Edge Not Found",
                    f"There is no edge between {first} and {node_id}.",
                    parent=self.root,
                )
                return

        self._clear_highlight()
        self.edit_selection = None

        if action == "add_edge":
            weight = simpledialog.askfloat(
                "Edge Weight",
                f"Enter weight for edge {first}–{node_id} (must be positive):",
                minvalue=0.1,
                parent=self.root,
            )
            if weight is None:
                self._update_status("Add edge canceled.")
                return
            try:
                self.graph.add_edge(first, node_id, weight)
            except ValueError as exc:
                messagebox.showerror("Add Edge", str(exc), parent=self.root)
                return
            self.reset_simulation(redraw=True)
            self._update_status(
                f"Added edge {first}–{node_id} with weight {self._format_weight(weight)}."
            )
            return

        if action == "remove_edge":
            try:
                self.graph.remove_edge(first, node_id)
            except ValueError as exc:
                messagebox.showerror("Remove Edge", str(exc), parent=self.root)
                return
            self.reset_simulation(redraw=True)
            self._update_status(f"Removed edge {first}–{node_id}.")
            return

        if action == "set_weight":
            weight = simpledialog.askfloat(
                "Update Weight",
                f"New weight for edge {first}–{node_id}:",
                minvalue=0.1,
                parent=self.root,
            )
            if weight is None:
                self._update_status("Weight update canceled.")
                return
            try:
                self.graph.set_edge_weight(first, node_id, weight)
            except KeyError:
                messagebox.showerror("Set Weight", f"Edge {first}–{node_id} does not exist.", parent=self.root)
                return
            self.reset_simulation(redraw=True)
            self._update_status(
                f"Updated weight for {first}–{node_id} to {self._format_weight(weight)}."
            )

    def _highlight_edit_node(self, node_id: str) -> None:
        if not self.canvas:
            return
        self._clear_highlight()
        if node_id in self.node_items:
            self.canvas.itemconfigure(self.node_items[node_id]["oval"], outline=COLOR_EDIT_SELECT, width=4)
            self.highlighted_node = node_id

    def _clear_highlight(self) -> None:
        if not self.canvas or not self.highlighted_node:
            self.highlighted_node = None
            return
        if self.highlighted_node in self.node_items:
            self.canvas.itemconfigure(self.node_items[self.highlighted_node]["oval"], outline="#0a1121", width=2)
        self.highlighted_node = None

    def _update_achievements_display(self) -> None:
        parts = [f"[{'x' if unlocked else ' '}] {name}" for name, unlocked in self.achievements.items()]
        self.achievements_var.set("Achievements: " + "  ".join(parts))

    def _unlock_achievement(self, name: str) -> bool:
        if self.achievements.get(name):
            return False
        self.achievements[name] = True
        self._update_achievements_display()
        return True

    def _add_tooltip(self, widget: tk.Widget, text: str) -> None:
        tooltip = Tooltip(widget, text)
        self.tooltips.append(tooltip)

    # ---------------------------------------------------------- Simulation flow
    def _make_explorer(self):
        algorithm_name = self.algorithm_var.get()
        explorer_cls = self.available_algorithms.get(algorithm_name, DijkstraExplorer)
        return explorer_cls(self.graph)

    def _prepare_steps(self) -> bool:
        if not self.start_node or not self.goal_node:
            self._update_status("Please assign both a start and goal node.")
            return False
        if self.start_node == self.goal_node:
            self._update_status("Start and goal are the same node. Pick a different goal.")
            return False
        self._clear_final_highlight(refresh=False)
        try:
            explorer = self._make_explorer()
            self.result = explorer.run(self.start_node, self.goal_node)
        except ValueError as exc:
            messagebox.showerror("Simulation Error", str(exc), parent=self.root)
            return False
        self.steps = self.result.steps
        self.step_index = -1
        algorithm_name = self.result.algorithm if self.result else self.algorithm_var.get()
        self._update_status(f"{algorithm_name} simulation ready. Watch the algorithm in action.")
        self.path_var.set("Path: —")
        self.cost_var.set("Cost: —")
        self._remove_traveler()
        return True

    def _animate_next_step(self) -> None:
        if self.step_index + 1 >= len(self.steps):
            self._on_simulation_complete()
            return
        self.step_index += 1
        step = self.steps[self.step_index]
        self._apply_step(step)
        delay = int(self.speed_var.get())
        self.animation_after = self.root.after(delay, self._animate_next_step)

    def compare_algorithms(self) -> None:
        if not self.start_node or not self.goal_node:
            messagebox.showinfo(
                "Algorithm Comparison",
                "Assign both a start and goal node before comparing algorithms.",
                parent=self.root,
            )
            return
        summaries: List[str] = []
        for name, explorer_cls in self.available_algorithms.items():
            explorer = explorer_cls(self.graph)
            try:
                result = explorer.run(self.start_node, self.goal_node)
            except ValueError as exc:
                summaries.append(f"{name}: error – {exc}")
                continue
            if result.negative_cycle:
                outcome = "negative cycle"
            elif math.isinf(result.cost):
                outcome = "unreachable"
            else:
                outcome = self._format_weight(result.cost)
            step_count = len(result.steps)
            summaries.append(f"{name}: {outcome} (steps {step_count})")
        comparison = "\n".join(summaries)
        message = (
            f"Comparison for {self.start_node} → {self.goal_node}:\n\n" + comparison
        )
        messagebox.showinfo("Algorithm Comparison", message, parent=self.root)

    def export_json(self) -> None:
        if not self.result:
            messagebox.showinfo(
                "Export JSON",
                "Run a simulation before exporting data.",
                parent=self.root,
            )
            return
        path = filedialog.asksaveasfilename(
            title="Save Run as JSON",
            defaultextension=".json",
            filetypes=[("JSON Files", "*.json"), ("All Files", "*.*")],
        )
        if not path:
            return

        def safe_number(value: float) -> float | str:
            return "inf" if math.isinf(value) else value

        payload = {
            "algorithm": self.result.algorithm,
            "cost": safe_number(self.result.cost),
            "path": self.result.path,
            "negative_cycle": self.result.negative_cycle,
            "steps": [
                {
                    "current": step.current,
                    "distances": {node: safe_number(distance) for node, distance in step.distances.items()},
                    "visited": step.visited,
                    "frontier": [(node, safe_number(priority)) for node, priority in step.frontier],
                    "previous": step.previous,
                    "relaxed_edge": step.relaxed_edge,
                    "iteration": step.iteration,
                    "notes": step.notes,
                }
                for step in self.result.steps
            ],
        }
        with open(path, "w", encoding="utf-8") as handle:
            json.dump(payload, handle, indent=2)
        self._update_status(f"Saved JSON export to {os.path.basename(path)}.")

    def export_gif(self) -> None:
        if not self.result:
            messagebox.showinfo(
                "Export GIF",
                "Run a simulation before exporting the animation.",
                parent=self.root,
            )
            return
        try:
            from PIL import Image, ImageDraw, ImageFont
        except ImportError:
            messagebox.showerror(
                "Export GIF",
                "Pillow is required for GIF export. Install it via 'pip install pillow'.",
                parent=self.root,
            )
            return

        path = filedialog.asksaveasfilename(
            title="Save Animation as GIF",
            defaultextension=".gif",
            filetypes=[("GIF Image", "*.gif"), ("All Files", "*.*")],
        )
        if not path:
            return

        width = int(self.canvas.winfo_width() or 720)
        height = int(self.canvas.winfo_height() or 620)
        node_positions = {
            node_id: self._project(info.position, width, height)
            for node_id, info in self.graph.nodes.items()
        }

        font = ImageFont.load_default()
        path_edges = set()
        if self.result.path:
            path_edges = {
                self._edge_key(self.result.path[i], self.result.path[i + 1])
                for i in range(len(self.result.path) - 1)
            }

        frames = []
        for index, step in enumerate(self.result.steps):
            highlight_path = index == len(self.result.steps) - 1 and bool(path_edges)
            frame = self._render_gif_frame(
                step,
                node_positions,
                width,
                height,
                font,
                path_edges if highlight_path else set(),
                Image,
                ImageDraw,
            )
            frames.append(frame)

        if not frames:
            messagebox.showinfo("Export GIF", "No frames to export.", parent=self.root)
            return

        duration = max(int(self.speed_var.get()), 150)
        frames[0].save(
            path,
            save_all=True,
            append_images=frames[1:],
            duration=duration,
            loop=0,
        )
        self._update_status(f"Saved GIF export to {os.path.basename(path)}.")

    def _apply_step(self, step: PathStep) -> None:
        if not self.canvas:
            return
        visited = set(step.visited)
        frontier = {node for node, _ in step.frontier}
        edge_width = self._edge_width()
        highlight_width = self._highlight_edge_width()
        for (source, target), line_id in self.edge_items.items():
            self.canvas.itemconfigure(line_id, fill=COLOR_EDGE, width=edge_width)

        if step.relaxed_edge:
            key = self._edge_key(step.relaxed_edge[0], step.relaxed_edge[1])
            if key in self.edge_items:
                self.canvas.itemconfigure(self.edge_items[key], fill=COLOR_EDGE_ACTIVE, width=highlight_width)

        for node_id, items in self.node_items.items():
            color = COLOR_DEFAULT_NODE
            if node_id in visited:
                color = COLOR_VISITED
            if node_id in frontier:
                color = COLOR_FRONTIER
            if step.current == node_id:
                color = COLOR_CURRENT
            if node_id == self.start_node:
                color = COLOR_START
            if node_id == self.goal_node:
                color = COLOR_GOAL
            self.canvas.itemconfigure(items["oval"], fill=color)

        current_label = "—"
        if step.current is not None:
            current_label = f"{step.current} ({self._node_name(step.current)})"
        self.current_info_var.set(f"Current: {current_label}")

        dist_lines: List[str] = []
        for node_id, distance in sorted(step.distances.items(), key=lambda item: item[1]):
            pretty = "∞" if math.isinf(distance) else self._format_weight(distance)
            dist_lines.append(f"{node_id}:{pretty}")
        self.distances_var.set("Distances → " + "  ".join(dist_lines))

        algorithm_name = self.result.algorithm if self.result else self.algorithm_var.get()
        if step.current is None:
            status = f"{algorithm_name}: initializing from {self._node_name(self.start_node)}."
        else:
            status = (
                f"{algorithm_name}: visiting {self._node_name(step.current)}. "
                f"Frontier size: {len(frontier)}."
            )
        if step.iteration is not None:
            status += f" (iteration {step.iteration})"
        if step.relaxed_edge:
            status += f" Relaxed edge {step.relaxed_edge[0]}→{step.relaxed_edge[1]}."
        if step.notes:
            status += f" {step.notes}"
        self._update_status(status)
        if self.final_path_edges:
            self._apply_final_highlight()

    def _on_simulation_complete(self) -> None:
        self._cancel_animation()
        if not self.result:
            return
        if self.result.negative_cycle:
            self._update_status(
                "Negative cycle detected. Shortest path is undefined for Bellman-Ford on this graph."
            )
            self.cost_var.set("Cost: undefined")
            self.path_var.set("Path: —")
            return
        if not self.result.path:
            self._update_status("No path found. Try randomizing weights or choosing new nodes.")
            self.cost_var.set("Cost: unreachable")
            self.path_var.set("Path: —")
            return
        cost_display = f"{self.result.cost:.0f}" if not math.isinf(self.result.cost) else "∞"
        self.cost_var.set(f"Cost: {cost_display}")
        node_names = [self._node_name(node_id) for node_id in self.result.path]
        self.path_var.set("Path: " + " → ".join(node_names))
        self.algorithms_used.add(self.result.algorithm)
        newly_unlocked: List[str] = []
        if self._unlock_achievement("First Run"):
            newly_unlocked.append("First Run")
        if len(self.algorithms_used) == len(self.available_algorithms):
            if self._unlock_achievement("Algorithm Explorer"):
                newly_unlocked.append("Algorithm Explorer")
        if not math.isinf(self.result.cost) and self.result.cost <= EFFICIENCY_TARGET:
            if self._unlock_achievement("Efficiency Star"):
                newly_unlocked.append("Efficiency Star")
        self._highlight_final_path(self.result.path)
        status_message = "Shortest path discovered! Enjoy the traversal animation."
        if newly_unlocked:
            status_message += " Achievements unlocked: " + ", ".join(newly_unlocked) + "."
        self._update_status(status_message)
        self._animate_traveler_along_path(self.result.path)

    # -------------------------------------------------------------- Node clicks
    def _on_node_clicked(self, node_id: str) -> None:
        mode = self.selection_mode.get()
        if mode == "start":
            self.start_node = node_id
        else:
            self.goal_node = node_id
        self.start_label.config(text=self._format_node_label("Start", self.start_node))
        self.goal_label.config(text=self._format_node_label("Goal", self.goal_node))
        self.reset_simulation()
        self._update_status(f"Selected {self._node_name(node_id)} as {'start' if mode == 'start' else 'goal'} node.")

    # ---------------------------------------------------------- Path animation
    def _render_gif_frame(
        self,
        step: PathStep,
        node_positions: Dict[str, Tuple[float, float]],
        width: int,
        height: int,
        font,
        path_edges: set[Tuple[str, str]],
        Image,
        ImageDraw,
    ):
        image = Image.new("RGB", (width, height), COLOR_CANVAS)
        draw = ImageDraw.Draw(image)
        visited = set(step.visited)
        frontier = {node for node, _ in step.frontier}
        relaxed_key = self._edge_key(*step.relaxed_edge) if step.relaxed_edge else None
        edge_width = max(2, int(round(4 * self.zoom_factor)))
        highlight_width = edge_width + 2
        radius = int(round(self._current_radius()))
        outline_width = max(2, int(round(self._node_outline_width())))

        for source, target, _ in self.graph.edges():
            key = self._edge_key(source, target)
            color = COLOR_EDGE_PATH if key in path_edges else COLOR_EDGE
            if relaxed_key and key == relaxed_key:
                color = COLOR_EDGE_ACTIVE
            x1, y1 = node_positions[source]
            x2, y2 = node_positions[target]
            current_width = highlight_width if key in path_edges or (relaxed_key and key == relaxed_key) else edge_width
            draw.line((x1, y1, x2, y2), fill=color, width=current_width)

        for node_id, (x, y) in node_positions.items():
            color = COLOR_DEFAULT_NODE
            if node_id in visited:
                color = COLOR_VISITED
            if node_id in frontier:
                color = COLOR_FRONTIER
            if step.current == node_id:
                color = COLOR_CURRENT
            if node_id == self.start_node:
                color = COLOR_START
            if node_id == self.goal_node:
                color = COLOR_GOAL
            draw.ellipse((x - radius, y - radius, x + radius, y + radius), fill=color, outline="#0a1121", width=outline_width)
            self._draw_centered_text(draw, (x, y), node_id, font, COLOR_TEXT_PRIMARY)

        return image

    @staticmethod
    def _draw_centered_text(draw, position: Tuple[float, float], text: str, font, fill: str) -> None:
        if hasattr(font, "getbbox"):
            bbox = font.getbbox(text)
            width = bbox[2] - bbox[0]
            height = bbox[3] - bbox[1]
        else:
            width, height = font.getsize(text)
        draw.text((position[0] - width / 2, position[1] - height / 2), text, font=font, fill=fill)

    def _apply_final_highlight_edges_only(self) -> None:
        if not self.canvas or not self.final_path_edges:
            return
        highlight_width = self._highlight_edge_width()
        for key in self.final_path_edges:
            line_id = self.edge_items.get(key)
            if line_id:
                self.canvas.itemconfigure(line_id, fill=COLOR_EDGE_PATH, width=highlight_width)

    def _apply_final_highlight(self) -> None:
        if not self.canvas:
            return
        if self.final_path_edges:
            self._apply_final_highlight_edges_only()
        outline_width = self._node_outline_width()
        for node_id in self.final_path_nodes:
            if node_id not in self.node_items:
                continue
            if node_id == self.start_node:
                fill = COLOR_START
            elif node_id == self.goal_node:
                fill = COLOR_GOAL
            else:
                fill = COLOR_PATH_NODE
            self.canvas.itemconfigure(self.node_items[node_id]["oval"], fill=fill, width=outline_width)
            self.canvas.tag_raise(self.node_items[node_id]["label"])
            self.canvas.tag_raise(self.node_items[node_id]["name"])

    def _clear_final_highlight(self, refresh: bool = True) -> None:
        if not (self.final_path_edges or self.final_path_nodes):
            return
        self.final_path_edges.clear()
        self.final_path_nodes.clear()
        if refresh and self.canvas:
            self._refresh_node_styles()

    def _highlight_final_path(self, path: List[str]) -> None:
        if not self.canvas or not path:
            return
        self.final_path_nodes = set(path)
        self.final_path_edges = {
            self._edge_key(path[index], path[index + 1]) for index in range(len(path) - 1)
        }
        self._apply_final_highlight()

    def _animate_traveler_along_path(self, path: List[str]) -> None:
        if len(path) < 2 or not self.canvas:
            return
        self._remove_traveler()
        start = path[0]
        x, y = self.node_positions[start]
        radius = max(6, min(16, 10 * self.zoom_factor))
        self.traveler_id = self.canvas.create_oval(
            x - radius,
            y - radius,
            x + radius,
            y + radius,
            fill="#38bdf8",
            outline="#0ea5e9",
            width=max(2, int(round(2 * self.zoom_factor))),
        )
        self._animate_traveler_segment(path, 0)

    def _animate_traveler_segment(self, path: List[str], index: int) -> None:
        if not self.canvas or not self.traveler_id:
            return
        if index >= len(path) - 1:
            return
        start = path[index]
        end = path[index + 1]
        start_pos = self.node_positions[start]
        end_pos = self.node_positions[end]
        steps = 24

        def move(step: int) -> None:
            if not self.canvas or not self.traveler_id:
                return
            t = step / steps
            x = start_pos[0] + (end_pos[0] - start_pos[0]) * t
            y = start_pos[1] + (end_pos[1] - start_pos[1]) * t
            radius = max(6, min(16, 10 * self.zoom_factor))
            self.canvas.coords(self.traveler_id, x - radius, y - radius, x + radius, y + radius)
            if step < steps:
                self.canvas.after(24, lambda: move(step + 1))
            else:
                self.canvas.after(160, lambda: self._animate_traveler_segment(path, index + 1))

        move(0)

    def _remove_traveler(self) -> None:
        if self.canvas and self.traveler_id:
            self.canvas.delete(self.traveler_id)
        self.traveler_id = None

    # ------------------------------------------------------------- Misc helpers
    def _cancel_animation(self) -> None:
        if self.animation_after is not None:
            self.root.after_cancel(self.animation_after)
            self.animation_after = None

    def _update_status(self, text: str) -> None:
        self.status_var.set(text)

    def _project(self, position: Tuple[float, float], width: int, height: int) -> Tuple[float, float]:
        padding_x = self.canvas_pad_x
        padding_y = self.canvas_pad_y
        base_x = padding_x + position[0] * max(width - 2 * padding_x, 1)
        base_y = padding_y + position[1] * max(height - 2 * padding_y, 1)
        center_x = width / 2
        center_y = height / 2
        zoom = self.zoom_factor
        x = center_x + (base_x - center_x) * zoom
        y = center_y + (base_y - center_y) * zoom
        return x, y

    def _normalize(self, x: float, y: float, width: int, height: int) -> Tuple[float, float]:
        center_x = width / 2
        center_y = height / 2
        zoom = self.zoom_factor if self.zoom_factor else 1.0
        base_x = center_x + (x - center_x) / zoom
        base_y = center_y + (y - center_y) / zoom
        denom_x = max(width - 2 * self.canvas_pad_x, 1)
        denom_y = max(height - 2 * self.canvas_pad_y, 1)
        nx = (base_x - self.canvas_pad_x) / denom_x
        ny = (base_y - self.canvas_pad_y) / denom_y
        nx = min(max(nx, 0.0), 1.0)
        ny = min(max(ny, 0.0), 1.0)
        return nx, ny

    @staticmethod
    def _edge_key(a: str, b: str) -> Tuple[str, str]:
        return tuple(sorted((a, b)))

    def _node_name(self, node_id: Optional[str]) -> str:
        if not node_id:
            return "—"
        return self.graph.nodes[node_id].label

    @staticmethod
    def _format_node_label(prefix: str, node: Optional[str]) -> str:
        return f"{prefix}: {node or '—'}"

    @staticmethod
    def _format_weight(weight: float) -> str:
        value = float(weight)
        if value.is_integer():
            return f"{value:.0f}"
        return f"{value:.2f}"


def run_app() -> None:
    root = tk.Tk()
    SimulatorApp(root)
    root.mainloop()
    def _snapshot_state(self) -> Tuple[WeightedGraph, Optional[str], Optional[str], set[str], set[Tuple[str, str]]]:
        return (
            self.graph.copy(),
            self.start_node,
            self.goal_node,
            set(self.final_path_nodes),
            set(self.final_path_edges),
        )

    def _push_undo(self) -> None:
        self.undo_stack.append(self._snapshot_state())
        if len(self.undo_stack) > 30:
            self.undo_stack.pop(0)

    def _restore_state(self, snapshot: Tuple[WeightedGraph, Optional[str], Optional[str], set[str], set[Tuple[str, str]]]) -> None:
        graph, start_node, goal_node, path_nodes, path_edges = snapshot
        self.graph = graph.copy()
        self.start_node = start_node
        self.goal_node = goal_node
        self.final_path_nodes = set(path_nodes)
        self.final_path_edges = set(path_edges)
        self.custom_node_index = max(
            [self.custom_node_index] + [int(node[1:]) + 1 for node in self.graph.nodes if node.startswith("N")],
        )
        self.start_label.config(text=self._format_node_label("Start", self.start_node))
        self.goal_label.config(text=self._format_node_label("Goal", self.goal_node))
        self.reset_simulation(redraw=True)

    def _on_undo(self, event: tk.Event) -> None:
        if not self.undo_stack:
            self._update_status("Nothing to undo.")
            return
        snapshot = self.undo_stack.pop()
        self._restore_state(snapshot)
        self._update_status("Undo applied.")
