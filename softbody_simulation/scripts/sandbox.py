import pygame
import numpy as np
from enum import Enum
from softbody_simulation.entities import GameObject, MassPoint, Spring, PolygonObstacle
from softbody_simulation.utils import distance_point_to_line


class Mode(Enum):
    PHYSICS_ALL = "physics_all"
    PHYSICS_MASS = "physics_mass"
    PHYSICS_SPRING = "physics_spring"
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

        self.selected_mass_points: list[MassPoint] = []
        self.selected_springs: list[Spring] = []
        self.selected_obstacles: list[PolygonObstacle] = []

        self.paused = False
        self.single_step = False

        self.drawing_obstacle = False
        self.obstacle_points = []

        # Current mode setting
        self.current_mode = Mode.PHYSICS_ALL

    # Mode management
    def toggle_mode(self):
        if self.is_physics_mode():
            self.current_mode = Mode.OBSTACLE
            self.clear_physics_selections()
        else:
            self.current_mode = Mode.PHYSICS_ALL
            self.cancel_obstacle_drawing()

    def is_physics_mode(self):
        """Check if currently in any physics mode."""
        return self.current_mode in [Mode.PHYSICS_ALL, Mode.PHYSICS_MASS, Mode.PHYSICS_SPRING]

    def update_mode_based_on_selection(self):
        """Update mode based on current selection state."""
        if not self.is_physics_mode():
            return
        
        if len(self.selected_springs) > 0:
            self.current_mode = Mode.PHYSICS_SPRING
        elif len(self.selected_mass_points) > 0:
            self.current_mode = Mode.PHYSICS_MASS
        else:
            self.current_mode = Mode.PHYSICS_ALL

    def get_current_mode_display_text(self):
        return "Physics" if self.is_physics_mode() else "Obstacle"

    # UI update functions
    def update_mass(self, value: float) -> None:
        self.default_mass = value
        for point in self.selected_mass_points:
            point.mass = value

    def update_stiffness(self, value: float) -> None:
        self.default_stiffness = value
        for spring in self.selected_springs:
            spring.stiffness = value

    def update_rest_length(self, value: float) -> None:
        self.default_rest_length = value
        for spring in self.selected_springs:
            spring.rest_length = value

    def update_damping(self, value: float) -> None:
        self.default_damping = value
        for spring in self.selected_springs:
            spring.damping = value

    def toggle_pause(self, key) -> None:
        self.paused = not self.paused

    def perform_single_step(self, key) -> None:
        if self.paused:
            self.single_step = True

    # Simulation input functions
    def handle_ctrl_left_click(self, mouse_pos) -> None:
        if not self.is_physics_mode():
            return

        # Check for mass point at click position
        mass_point = self._get_mass_point_at(mouse_pos)
        if mass_point:
            # Toggle mass point selection
            if mass_point in self.selected_mass_points:
                self.selected_mass_points.remove(mass_point)
            else:
                self.selected_mass_points.append(mass_point)
            self.update_mode_based_on_selection()
            return

        # Check for spring at click position
        spring = self._get_spring_at(mouse_pos)
        if spring:
            # Toggle spring selection
            if spring in self.selected_springs:
                self.selected_springs.remove(spring)
            else:
                self.selected_springs.append(spring)
            self.update_mode_based_on_selection()
            return

    def handle_left_click(self, mouse_pos) -> None:
        if self.is_physics_mode():
            self._handle_physics_left_click(mouse_pos)
        else:
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

        # If nothing hit, clear selections
        self.clear_all_selections()

    def _handle_obstacle_left_click(self, mouse_pos) -> None:
        if self.drawing_obstacle:
            self.obstacle_points.append(np.array(mouse_pos))
        else:
            obstacle = self.get_obstacle_at(mouse_pos)
            if obstacle:
                self.select_obstacle(obstacle)
            else:
                # Start drawing a new obstacle
                self.drawing_obstacle = True
                self.obstacle_points = [np.array(mouse_pos)]

    def _handle_left_click_mass_point(self, mass_point) -> None:
        self.selected_springs = []
        self.selected_obstacles = []

        if mass_point in self.selected_mass_points:
            self.selected_mass_points.remove(mass_point)
        elif self.selected_mass_points:
            # Create springs between selected points and the new point
            for selected in self.selected_mass_points:
                if not self._spring_exists(mass_point, selected):
                    new_spring = Spring(
                        (mass_point, selected),
                        stiffness=self.default_stiffness,
                        damping=self.default_damping,
                        rest_length=self.default_rest_length,
                    )
                    self.springs.append(new_spring)
            self.selected_mass_points = []
        else:
            self.selected_mass_points = [mass_point]
        
        self.update_mode_based_on_selection()

    def _handle_left_click_spring(self, spring) -> None:
        self.selected_mass_points = []
        self.selected_obstacles = []

        if spring in self.selected_springs:
            self.selected_springs.remove(spring)
        else:
            self.selected_springs = [spring]
        
        self.update_mode_based_on_selection()

    def handle_right_click(self, mouse_pos) -> None:
        """Handle right click in current mode."""
        if self.is_physics_mode():
            # Create a new mass point
            new_point = MassPoint(np.array(mouse_pos), self.default_mass)
            self.mass_points.append(new_point)
        else:  # Obstacle mode
            if self.drawing_obstacle and len(self.obstacle_points) >= 3:
                self.complete_obstacle()

    def _handle_left_click_obstacle(self, obstacle) -> None:
        self.selected_mass_points = []
        self.selected_springs = []

        if obstacle in self.selected_obstacles:
            return

        self.selected_obstacles = [obstacle]

    def select_obstacle(self, obstacle) -> None:
        self.selected_mass_points = []
        self.selected_springs = []

        if obstacle in self.selected_obstacles and len(self.selected_obstacles) == 1:
            pass
        else:
            self.selected_obstacles = [obstacle]

    def clear_all_selections(self) -> None:
        self.selected_mass_points = []
        self.selected_springs = []
        self.selected_obstacles = []
        self.update_mode_based_on_selection()

    def clear_physics_selections(self) -> None:
        self.selected_mass_points = []
        self.selected_springs = []
        self.update_mode_based_on_selection()

    def _spring_exists(self, mass_point_a, mass_point_b) -> bool:
        return any(
            spring
            for spring in self.springs
            if mass_point_a in [spring.a, spring.b]
            and mass_point_b in [spring.a, spring.b]
        )

    def handle_delete(self) -> None:
        # Delete mass points and connected springs
        if self.selected_mass_points:
            for point in self.selected_mass_points:
                self.mass_points.remove(point)

            # Remove any springs connected to deleted points
            self.springs = [
                spring
                for spring in self.springs
                if not any(
                    point in [spring.a, spring.b] for point in self.selected_mass_points
                )
            ]

            # Update spring selection to remove any deleted springs
            self.selected_springs = [
                spring for spring in self.selected_springs if spring in self.springs
            ]

            self.selected_mass_points = []

        # Delete selected springs
        if self.selected_springs:
            for spring in self.selected_springs:
                if spring in self.springs:  # Check if not already removed
                    self.springs.remove(spring)
            self.selected_springs = []
        
        self.update_mode_based_on_selection()

    def handle_escape_keydown(self, key) -> None:
        if self.drawing_obstacle:
            self.drawing_obstacle = False
            self.obstacle_points = []
        else:
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

    def get_obstacle_at(self, pos, threshold: int = 10) -> PolygonObstacle | None:
        for obstacle in self.obstacles:
            # Check if point is inside obstacle or near its boundary
            if obstacle.contains_point(np.array(pos)) or obstacle.near_boundary(
                np.array(pos), threshold
            ):
                return obstacle
        return None

    def complete_obstacle(self):
        if len(self.obstacle_points) >= 3:
            new_obstacle = PolygonObstacle(np.array(self.obstacle_points))
            self.obstacles.append(new_obstacle)

            # Clear existing obstacle selection and select the new one
            self.selected_obstacles = [new_obstacle]

        self.drawing_obstacle = False
        self.obstacle_points = []

    def delete_selected_obstacles(self):
        if self.selected_obstacles:
            for obstacle in self.selected_obstacles:
                if obstacle in self.obstacles:  # Check if not already removed
                    self.obstacles.remove(obstacle)
            self.selected_obstacles = []
        elif self.obstacles:  # If no selection, remove the last added obstacle
            self.obstacles.pop()

    def get_obstacle_drawing_state(self) -> tuple[bool, list[np.ndarray]]:
        return self.drawing_obstacle, self.obstacle_points

    def cancel_obstacle_drawing(self):
        self.drawing_obstacle = False
        self.obstacle_points = []

    # Update simulation state
    def update(self, delta_time: float) -> None:
        GameObject.set_delta_time(delta_time)

        if self.paused:
            if self.single_step:
                self._update_simulation()
                self.single_step = False
        else:
            self._update_simulation()

    def _update_simulation(self) -> None:
        for spring in self.springs:
            spring.update()
        for point in self.mass_points:
            others = [m for m in self.mass_points if m != point]
            point.update(self.obstacles, others)
