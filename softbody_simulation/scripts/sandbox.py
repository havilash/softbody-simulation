import pygame
import numpy as np
from enum import Enum
from softbody_simulation.entities import GameObject, MassPoint, Spring, PolygonObstacle
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
    def __init__(
        self,
        default_mass: float,
        default_stiffness: float,
        default_rest_length: float,
        default_damping: float,
    ):
        self.default_mass = default_mass
        self.default_stiffness = default_stiffness
        self.default_rest_length = default_rest_length
        self.default_damping = default_damping

        self.mass_points: list[MassPoint] = []
        self.springs: list[Spring] = []
        self.obstacles: list[PolygonObstacle] = []

        self.selection = Selection.NONE

        self.paused = False
        self.single_step = False

        self.drawing_obstacle = False
        self.drawing_obstacle_points = []

        self.mode = Mode.PHYSICS

    def switch_mode(self, mode: Mode):
        self.clear_all_selections()

        self.drawing_obstacle = False
        self.drawing_obstacle_points = []

        self.mode = mode

    def _update_selection(self):
        if any(spring.selected for spring in self.springs):
            self.selection = Selection.SPRING
        elif any(point.selected for point in self.mass_points):
            self.selection = Selection.MASS_POINT
        elif any(obstacle.selected for obstacle in self.obstacles):
            self.selection = Selection.OBSTACLE
        else:
            self.selection = Selection.NONE

    # UI update functions
    def update_mass(self, value: float) -> None:
        self.default_mass = value
        for point in self.mass_points:
            if point.selected:
                point.mass = value

    def update_stiffness(self, value: float) -> None:
        self.default_stiffness = value
        for spring in self.springs:
            if spring.selected:
                spring.stiffness = value

    def update_rest_length(self, value: float) -> None:
        self.default_rest_length = value
        for spring in self.springs:
            if spring.selected:
                spring.rest_length = value

    def update_damping(self, value: float) -> None:
        self.default_damping = value
        for spring in self.springs:
            if spring.selected:
                spring.damping = value

    def toggle_pause(self) -> None:
        self.paused = not self.paused

    def perform_single_step(self) -> None:
        if self.paused:
            self.single_step = True

    # Simulation input functions
    def handle_ctrl_left_click(self, mouse_pos) -> None:
        if not self.mode == Mode.PHYSICS:
            return

        mass_point = self._get_mass_point_at(mouse_pos)
        if mass_point:
            mass_point.selected = not mass_point.selected
            self._update_selection()
            return

        spring = self._get_spring_at(mouse_pos)
        if spring:
            spring.selected = not spring.selected
            self._update_selection()
            return

    def handle_left_click(self, mouse_pos) -> None:
        match self.mode:
            case Mode.PHYSICS:
                self._handle_physics_left_click(mouse_pos)
            case Mode.OBSTACLE:
                self._handle_obstacle_left_click(mouse_pos)

    def _handle_physics_left_click(self, mouse_pos) -> None:
        mass_point = self._get_mass_point_at(mouse_pos)
        if mass_point:
            self._handle_left_click_mass_point(mass_point)
            return

        spring = self._get_spring_at(mouse_pos)
        if spring:
            self._handle_left_click_spring(spring)
            return

        self.clear_all_selections()

    def _handle_obstacle_left_click(self, mouse_pos) -> None:
        if self.drawing_obstacle:
            self.drawing_obstacle_points.append(np.array(mouse_pos))
        else:
            obstacle = self._get_obstacle_at(mouse_pos)
            if obstacle:
                for p in self.mass_points:
                    p.selected = False
                for s in self.springs:
                    s.selected = False

                for obs in self.obstacles:
                    obs.selected = False
                obstacle.selected = True
            else:
                self.drawing_obstacle = True
                self.drawing_obstacle_points = [np.array(mouse_pos)]

    def _handle_left_click_mass_point(self, mass_point) -> None:
        for spring in self.springs:
            spring.selected = False
        for obs in self.obstacles:
            obs.selected = False

        selected_mass_points = [p for p in self.mass_points if p.selected]

        if mass_point.selected:
            mass_point.selected = False
        elif selected_mass_points:
            # Create springs between the already selected mass points and the new mass point
            for selected in selected_mass_points:
                if not self._spring_exists(mass_point, selected):
                    new_spring = Spring(
                        (mass_point, selected),
                        stiffness=self.default_stiffness,
                        damping=self.default_damping,
                        rest_length=self.default_rest_length,
                    )
                    self.springs.append(new_spring)

            for p in selected_mass_points:
                p.selected = False
        else:
            mass_point.selected = True

        self._update_selection()

    def _handle_left_click_spring(self, spring) -> None:
        for p in self.mass_points:
            p.selected = False
        for obs in self.obstacles:
            obs.selected = False

        if spring.selected:
            spring.selected = False
        else:
            for s in self.springs:
                s.selected = False

            spring.selected = True

        self._update_selection()

    def _handle_left_click_obstacle(self, obstacle) -> None:
        # Deselect masses and springs
        for p in self.mass_points:
            p.selected = False
        for s in self.springs:
            s.selected = False

        # Toggle obstacle selection: if already selected, do nothing; else select it exclusively.
        if not obstacle.selected:
            for obs in self.obstacles:
                obs.selected = False
            obstacle.selected = True

    def handle_right_click(self, mouse_pos) -> None:
        """Handle right click in current mode."""
        if self.mode == Mode.PHYSICS:
            # Create a new mass point (ensure its selected flag is False)
            new_point = MassPoint(np.array(mouse_pos), self.default_mass)
            new_point.selected = False
            self.mass_points.append(new_point)
        else:  # Obstacle mode
            if self.drawing_obstacle and len(self.drawing_obstacle_points) >= 3:
                self.complete_obstacle()

    def clear_all_selections(self) -> None:
        for p in self.mass_points:
            p.selected = False
        for s in self.springs:
            s.selected = False
        for obs in self.obstacles:
            obs.selected = False
        self._update_selection()

    def _spring_exists(self, mass_point_a, mass_point_b) -> bool:
        return any(
            spring
            for spring in self.springs
            if mass_point_a in [spring.a, spring.b]
            and mass_point_b in [spring.a, spring.b]
        )

    def handle_delete_keydown(self):
        match self.selection:
            case Selection.MASS_POINT:
                selected_mass_points = [p for p in self.mass_points if p.selected]
                for point in selected_mass_points:
                    self.mass_points.remove(point)
                self.springs = [
                    spring
                    for spring in self.springs
                    if not (spring.a in selected_mass_points or spring.b in selected_mass_points)
                ]

            case Selection.SPRING:
                selected_springs = [s for s in self.springs if s.selected]
                for spring in selected_springs:
                    if spring in self.springs:
                        self.springs.remove(spring)

            case Selection.OBSTACLE:
                selected_obstacles = [obs for obs in self.obstacles if obs.selected]
                for obstacle in selected_obstacles:
                    if obstacle in self.obstacles:
                        self.obstacles.remove(obstacle)

        self._update_selection()


    def handle_escape_keydown(self) -> None:
        self.drawing_obstacle = False
        self.drawing_obstacle_points = []
        self.clear_all_selections()

    def _get_mass_point_at(self, pos, radius: int = 10) -> MassPoint | None:
        for point in self.mass_points:
            if np.linalg.norm(point.pos - np.array(pos)) <= radius:
                return point
        return None

    def _get_spring_at(self, pos, threshold: int = 5) -> Spring | None:
        for spring in self.springs:
            p1, p2 = spring.a.pos, spring.b.pos
            if distance_point_to_line(np.array(pos), (p1, p2)) <= threshold:
                return spring
        return None

    def _get_obstacle_at(self, pos, threshold: int = 10) -> PolygonObstacle | None:
        for obstacle in self.obstacles:
            if obstacle.contains_point(np.array(pos)) or obstacle.near_boundary(
                np.array(pos), threshold
            ):
                return obstacle
        return None

    def complete_obstacle(self):
        if len(self.drawing_obstacle_points) >= 3:
            new_obstacle = PolygonObstacle(np.array(self.drawing_obstacle_points))
            new_obstacle.selected = True  # Mark the new obstacle as selected
            self.obstacles.append(new_obstacle)
            # Deselect other obstacles
            for obs in self.obstacles:
                if obs is not new_obstacle:
                    obs.selected = False
        self.drawing_obstacle = False
        self.drawing_obstacle_points = []

    # Update simulation state
    def update(self, delta_time: float) -> None:
        if self.paused:
            if self.single_step:
                self._update_simulation(delta_time)
                self.single_step = False
        else:
            self._update_simulation(delta_time)

    def _update_simulation(self, delta_time: float) -> None:
        for spring in self.springs:
            spring.update(delta_time)
        for point in self.mass_points:
            others = [m for m in self.mass_points if m != point]
            point.update(delta_time, self.obstacles, others)
