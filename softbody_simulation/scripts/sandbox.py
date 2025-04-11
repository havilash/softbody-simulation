import pygame
import numpy as np
from enum import Enum
from softbody_simulation.consts import DRAG_THRESHOLD_MS
from softbody_simulation.entities import MassPoint, Spring, PolygonObstacle
from softbody_simulation.utils import distance_point_to_line


class Selection(Enum):
    NONE = "none"
    MASS_POINT = "mass_point"
    SPRING = "spring"
    OBSTACLE = "obstacle"


class Mode(Enum):
    PHYSICS = "physics"
    OBSTACLE = "obstacle"


class Sandbox:
    def __init__(self, default_mass: float, default_stiffness: float,
                 default_rest_length: float, default_damping: float):
        self.default_mass = default_mass
        self.default_stiffness = default_stiffness
        self.default_rest_length = default_rest_length
        self.default_damping = default_damping
        self.use_gravity = True

        self.mass_points: list[MassPoint] = []
        self.springs: list[Spring] = []
        self.obstacles: list[PolygonObstacle] = []

        self.selection = Selection.NONE
        self.mode = Mode.PHYSICS

        self.paused = False
        self.single_step = False

        self.drawing_obstacle = False
        self.drawing_obstacle_points = []

        self.drag_time = None
        self.drag_initial_mouse = None
        self.drag_initial_positions = {}

    # --- Helper Functions for Selection Operations ---
    def _deselect_all(self, items: list) -> None:
        for item in items:
            item.selected = False

    def _clear_all_selections(self) -> None:
        self._deselect_all(self.mass_points)
        self._deselect_all(self.springs)
        self._deselect_all(self.obstacles)
        self.selection = Selection.NONE

    def _update_defaults_for_item(self, item) -> None:
        if isinstance(item, MassPoint):
            self.default_mass = item.mass
            self.selection = Selection.MASS_POINT
        elif isinstance(item, Spring):
            self.default_stiffness = item.stiffness
            self.default_rest_length = item.rest_length
            self.default_damping = item.damping
            self.selection = Selection.SPRING
        elif isinstance(item, PolygonObstacle):
            self.selection = Selection.OBSTACLE

    def _select_item(self, item) -> None:
        if isinstance(item, MassPoint):
            self._deselect_all(self.springs)
            self._deselect_all(self.obstacles)
        elif isinstance(item, Spring):
            self._deselect_all(self.mass_points)
            self._deselect_all(self.obstacles)
        elif isinstance(item, PolygonObstacle):
            self._deselect_all(self.mass_points)
            self._deselect_all(self.springs)
        item.selected = True
        self._update_defaults_for_item(item)

    def _toggle_item_selection(self, item) -> None:
        if isinstance(item, MassPoint):
            self._deselect_all(self.springs)
            self._deselect_all(self.obstacles)
        elif isinstance(item, Spring):
            self._deselect_all(self.mass_points)
            self._deselect_all(self.obstacles)
        elif isinstance(item, PolygonObstacle):
            self._deselect_all(self.mass_points)
            self._deselect_all(self.springs)
        item.selected = not item.selected
        if item.selected:
            self._update_defaults_for_item(item)
    
    # --- Helper Functions for Dragging ---
    def _start_drag(self, mouse_pos) -> None:
        self.drag_time = pygame.time.get_ticks()
        self.drag_initial_mouse = mouse_pos
        self.drag_initial_positions.clear()

    def _update_drag(self, current_pos) -> None:
        delta = np.array(current_pos) - np.array(self.drag_initial_mouse)
        for item, initial in self.drag_initial_positions.items():
            item.pos = initial + delta

    def _end_drag(self) -> None:
        self.drag_time = None
        self.drag_initial_mouse = None
        self.drag_initial_positions.clear()

    # --- Mode Switching and Reset ---
    def switch_mode(self, mode: Mode):
        self._clear_all_selections()
        self.drawing_obstacle = False
        self.drawing_obstacle_points = []
        self.mode = mode

    def reset_simulation(self) -> None:
        self._clear_all_selections()
        self.mass_points.clear()
        self.springs.clear()
        self.obstacles.clear()

    # --- Slider Callbacks ---
    def update_mass(self, value: float) -> None:
        self.default_mass = value
        for p in self.mass_points:
            if p.selected:
                p.mass = value

    def update_stiffness(self, value: float) -> None:
        self.default_stiffness = value
        for s in self.springs:
            if s.selected:
                s.stiffness = value

    def update_rest_length(self, value: float) -> None:
        self.default_rest_length = value
        for s in self.springs:
            if s.selected:
                s.rest_length = value

    def update_damping(self, value: float) -> None:
        self.default_damping = value
        for s in self.springs:
            if s.selected:
                s.damping = value

    def toggle_pause(self) -> None:
        self.paused = not self.paused

    def perform_single_step(self) -> None:
        if self.paused:
            self.single_step = True

    # --- Event Handler Methods ---
    def toggle_gravity(self) -> None:
        self.use_gravity = not self.use_gravity
        for p in self.mass_points:
            p.use_gravity = self.use_gravity

    def handle_double_click(self, mouse_pos) -> None:
        self._end_drag()
        if self.mode == Mode.PHYSICS:
            mass_point = self._get_mass_point_at(mouse_pos)
            if mass_point:
                self._deselect_all(self.springs)
                self._deselect_all(self.obstacles)
                for p in self.mass_points:
                    p.selected = True
                self.selection = Selection.MASS_POINT
                self.default_mass = mass_point.mass
                return
            spring = self._get_spring_at(mouse_pos)
            if spring:
                self._deselect_all(self.mass_points)
                self._deselect_all(self.obstacles)
                for s in self.springs:
                    s.selected = True
                self.selection = Selection.SPRING
                self.default_stiffness = spring.stiffness
                self.default_rest_length = spring.rest_length
                self.default_damping = spring.damping
        elif self.mode == Mode.OBSTACLE:
            obstacle = self._get_obstacle_at(mouse_pos)
            if obstacle:
                self._deselect_all(self.mass_points)
                self._deselect_all(self.springs)
                for o in self.obstacles:
                    o.selected = True
                self.selection = Selection.OBSTACLE

    def handle_ctrl_click(self, mouse_pos) -> None:
        self._end_drag()
        if self.mode == Mode.PHYSICS:
            mass_point = self._get_mass_point_at(mouse_pos)
            if mass_point:
                self._toggle_item_selection(mass_point)
                return
            spring = self._get_spring_at(mouse_pos)
            if spring:
                self._toggle_item_selection(spring)
                return
        elif self.mode == Mode.OBSTACLE:
            obstacle = self._get_obstacle_at(mouse_pos)
            if obstacle:
                self._toggle_item_selection(obstacle)
                return

    def handle_left_mouse_down(self, mouse_pos) -> None:
        self._start_drag(mouse_pos)
        if self.mode == Mode.OBSTACLE:
            self._handle_obstacle_click(mouse_pos)
            self._end_drag()

    def handle_left_mouse_up(self, mouse_pos) -> None:
        if self.drag_time is None:
            return
        current_time = pygame.time.get_ticks()
        if self.mode == Mode.PHYSICS and current_time - self.drag_time < DRAG_THRESHOLD_MS:
            self._process_physics_click(mouse_pos)
        self._end_drag()

    def handle_mouse_drag(self, mouse_pos) -> None:
        if self.drag_time is None:
            return
        current_time = pygame.time.get_ticks()
        if current_time - self.drag_time < DRAG_THRESHOLD_MS:
            return
        if self.drag_initial_mouse is None:
            self.drag_initial_mouse = mouse_pos
            mass_point = self._get_mass_point_at(mouse_pos)
            if mass_point:
                self._select_item(mass_point)
            for p in (p for p in self.mass_points if p.selected):
                self.drag_initial_positions[p] = p.pos.copy()
        self._update_drag(mouse_pos)

    def handle_right_mouse_click(self, mouse_pos) -> None:
        if self.mode == Mode.PHYSICS:
            new_point = MassPoint(np.array(mouse_pos), self.default_mass,
                                  use_gravity=self.use_gravity)
            new_point.selected = False
            self.mass_points.append(new_point)
        elif self.drawing_obstacle and len(self.drawing_obstacle_points) >= 3:
            self.complete_obstacle()

    def handle_escape(self) -> None:
        self.drawing_obstacle = False
        self.drawing_obstacle_points = []
        self._clear_all_selections()

    def handle_delete(self) -> None:
        if self.selection == Selection.MASS_POINT:
            selected = [p for p in self.mass_points if p.selected]
            for p in selected:
                self.mass_points.remove(p)
            self.springs = [s for s in self.springs if s.a not in selected and s.b not in selected]
        elif self.selection == Selection.SPRING:
            for s in [s for s in self.springs if s.selected]:
                if s in self.springs:
                    self.springs.remove(s)
        elif self.selection == Selection.OBSTACLE:
            for o in [o for o in self.obstacles if o.selected]:
                if o in self.obstacles:
                    self.obstacles.remove(o)
        self.selection = Selection.NONE

    # --- Processing Clicks ---
    def _process_physics_click(self, mouse_pos) -> None:
        mass_point = self._get_mass_point_at(mouse_pos)
        if mass_point:
            self._handle_mass_point_click(mass_point)
            return
        spring = self._get_spring_at(mouse_pos)
        if spring:
            self._handle_spring_click(spring)
            return
        self._clear_all_selections()

    def _handle_mass_point_click(self, mass_point) -> None:
        self._deselect_all(self.springs)
        self._deselect_all(self.obstacles)
        selected = [p for p in self.mass_points if p.selected]
        if mass_point.selected and selected:
            mass_point.selected = False
        elif selected:
            for sel in selected:
                if not self._spring_exists(mass_point, sel):
                    self.springs.append(
                        Spring((mass_point, sel),
                               stiffness=self.default_stiffness,
                               damping=self.default_damping,
                               rest_length=self.default_rest_length)
                    )
            self._deselect_all(selected)
        else:
            self._select_item(mass_point)
        selected = [p for p in self.mass_points if p.selected]
        self.drag_initial_positions = {p: p.pos.copy() for p in selected}

    def _handle_spring_click(self, spring) -> None:
        self._deselect_all(self.mass_points)
        self._deselect_all(self.obstacles)
        if spring.selected:
            spring.selected = False
        else:
            self._select_item(spring)

    def _handle_obstacle_click(self, mouse_pos) -> None:
        if self.drawing_obstacle:
            if len(self.drawing_obstacle_points) >= 3 and \
               np.linalg.norm(mouse_pos - self.drawing_obstacle_points[0]) < 10:
                self.complete_obstacle()
                return
            self.drawing_obstacle_points.append(np.array(mouse_pos))
        else:
            obstacle = self._get_obstacle_at(mouse_pos)
            if obstacle:
                self._clear_all_selections()
                obstacle.selected = True
            else:
                self.drawing_obstacle = True
                self.drawing_obstacle_points = [np.array(mouse_pos)]

    def complete_obstacle(self):
        if len(self.drawing_obstacle_points) >= 3:
            new_obs = PolygonObstacle(np.array(self.drawing_obstacle_points))
            new_obs.selected = True
            self.obstacles.append(new_obs)
            for obs in self.obstacles:
                if obs is not new_obs:
                    obs.selected = False
        self.drawing_obstacle = False
        self.drawing_obstacle_points = []

    # --- Helper Methods ---
    def _get_mass_point_at(self, pos, radius: int = 10) -> MassPoint | None:
        pos = np.array(pos)
        for point in self.mass_points:
            if np.linalg.norm(point.pos - pos) <= radius:
                return point
        return None

    def _get_spring_at(self, pos, threshold: int = 5) -> Spring | None:
        pos = np.array(pos)
        for spring in self.springs:
            p1, p2 = spring.a.pos, spring.b.pos
            if distance_point_to_line(pos, (p1, p2)) <= threshold:
                return spring
        return None

    def _get_obstacle_at(self, pos, threshold: int = 10) -> PolygonObstacle | None:
        pos = np.array(pos)
        for obstacle in self.obstacles:
            if obstacle.contains_point(pos) or obstacle.near_boundary(pos, threshold):
                return obstacle
        return None

    def _spring_exists(self, mass_point_a, mass_point_b) -> bool:
        return any(mass_point_a in (s.a, s.b) and mass_point_b in (s.a, s.b)
                   for s in self.springs)

    def _reset_drag_state(self):
        self.drag_time = None
        self.drag_initial_mouse = None
        self.drag_initial_positions.clear()

    # --- Update Simulation ---
    def update(self, delta_time: float) -> None:
        if self.paused:
            if self.single_step:
                self._update_simulation(delta_time)
                self.single_step = False
        else:
            self._update_simulation(delta_time)

    def _update_simulation(self, delta_time: float) -> None:
        for s in self.springs:
            s.update(delta_time)
        for p in self.mass_points:
            others = [other for other in self.mass_points if other is not p]
            p.update(delta_time, self.obstacles, others)
