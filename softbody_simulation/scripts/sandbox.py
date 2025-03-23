import pygame
from typing import List, Optional, Tuple, Set
import numpy as np
from consts import WIN_SIZE
from softbody_simulation.entities import GameObject, MassPoint, Spring, PolygonObstacle
from softbody_simulation.utils import distance_point_to_line


class SandboxScript:
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

        self.mass_points: List[MassPoint] = []
        self.springs: List[Spring] = []
        self.obstacles: List[PolygonObstacle] = []

        # Replace single selection with multiple selection
        self.selected_mass_points: List[MassPoint] = []
        self.selected_springs: List[Spring] = []
        self.selected_obstacles: List[PolygonObstacle] = []

        self.paused = False
        self.single_step = False

        self.drawing_obstacle = False
        self.obstacle_points = []

        # For connection mode (when first mass point is selected)
        self.connecting = False

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

    def toggle_pause(self, screen: pygame.Surface) -> None:
        self.paused = not self.paused

    def perform_single_step(self, screen: pygame.Surface) -> None:
        if self.paused:
            self.single_step = True

    # Simulation input functions
    def handle_ctrl_left_click(self, mouse_pos) -> None:
        # TODO: implement multiselect

    def handle_left_click(self, mouse_pos) -> None:
        mass_point = self._get_mass_point_at(mouse_pos)

        if mass_point:
            self._handle_left_click_mass_point(mass_point)
            return

        spring = self._get_spring_at(mouse_pos)
        if spring:
            self._handle_left_click_spring(spring)
            return

        obstacle = self.get_obstacle_at(mouse_pos)
        if obstacle:
            self._handle_left_click_obstacle(obstacle)
            return

        self.clear_all_selections()

    def _handle_left_click_mass_point(self, mass_point) -> None:
        self.selected_springs = []
        self.selected_obstacles = []

        if mass_point in self.selected_mass_points:
            self.selected_mass_points.remove(mass_point)
            return

        if self.selected_mass_points:
            for selected in self.selected_mass_points:
                new_spring = Spring(
                    (mass_point, selected),
                    stiffness=self.default_stiffness,
                    damping=self.default_damping,
                    rest_length=self.default_rest_length,
                )
                self.springs.append(new_spring)
            self.selected_mass_points = []
            return

        self.selected_mass_points = [mass_point]

    def _handle_left_click_spring(self, spring) -> None:
        self.selected_mass_points = []
        self.selected_obstacles = []

        if spring in self.selected_springs:
            self.selected_springs.remove(spring)
            return

        self.selected_springs.append(spring)

    def _handle_left_click_obstacle(self, obstacle) -> None:
        self.selected_mass_points = []
        self.selected_springs = []

        if obstacle in self.selected_obstacles:
            return

        self.selected_obstacles.append(obstacle)

    def select_obstacle(self, obstacle) -> None:
        """Select an obstacle, clearing other selections."""
        self.selected_mass_points = []
        self.selected_springs = []

        if obstacle in self.selected_obstacles and len(self.selected_obstacles) == 1:
            # Already selected - do nothing
            pass
        else:
            # Clear existing obstacle selections and select the new one
            self.selected_obstacles = [obstacle]

    def clear_all_selections(self) -> None:
        """Clear all selections."""
        self.selected_mass_points = []
        self.selected_springs = []
        self.selected_obstacles = []

    def clear_physics_selections(self) -> None:
        """Clear physics-related selections."""
        self.selected_mass_points = []
        self.selected_springs = []

    def _spring_exists(self, mass_point_a, mass_point_b) -> bool:
        return any(
            spring
            for spring in self.springs
            if mass_point_a in [spring.a, spring.b]
            and mass_point_b in [spring.a, spring.b]
        )

    def handle_delete(self) -> None:
        """Delete all selected objects."""
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

    def handle_right_click(self, mouse_pos) -> None:
        new_point = MassPoint(np.array(mouse_pos), self.default_mass)
        self.mass_points.append(new_point)

    def handle_escape_keydown(self, key) -> None:
        if self.drawing_obstacle:
            self.drawing_obstacle = False
            self.obstacle_points = []
        else:
            self.clear_all_selections()

    def _get_mass_point_at(self, pos, radius: int = 10) -> Optional[MassPoint]:
        for point in self.mass_points:
            if np.linalg.norm(point.pos - np.array(pos)) <= radius:
                return point
        return None

    def _get_spring_at(self, pos, threshold: int = 5) -> Optional[Spring]:
        for spring in self.springs:
            p1, p2 = spring.a.pos, spring.b.pos
            if distance_point_to_line(np.array(pos), (p1, p2)) <= threshold:
                return spring
        return None

    def get_obstacle_at(self, pos, threshold: int = 10) -> Optional[PolygonObstacle]:
        """Find an obstacle at the given position."""
        for obstacle in self.obstacles:
            # Check if point is inside obstacle or near its boundary
            if obstacle.contains_point(np.array(pos)) or obstacle.near_boundary(
                np.array(pos), threshold
            ):
                return obstacle
        return None

    # Obstacle creation methods
    def handle_obstacle_click(self, pos):
        if not self.drawing_obstacle:
            self.drawing_obstacle = True
            self.obstacle_points = [np.array(pos)]
        else:
            self.obstacle_points.append(np.array(pos))

    def complete_obstacle(self):
        if len(self.obstacle_points) >= 3:
            new_obstacle = PolygonObstacle(np.array(self.obstacle_points))
            self.obstacles.append(new_obstacle)

            # Clear existing obstacle selection and select the new one
            self.selected_obstacles = [new_obstacle]

        self.drawing_obstacle = False
        self.obstacle_points = []

    def delete_selected_obstacles(self):
        """Delete all selected obstacles."""
        if self.selected_obstacles:
            for obstacle in self.selected_obstacles:
                if obstacle in self.obstacles:  # Check if not already removed
                    self.obstacles.remove(obstacle)
            self.selected_obstacles = []
        elif self.obstacles:  # If no selection, remove the last added obstacle
            self.obstacles.pop()

    def get_obstacle_drawing_state(self) -> Tuple[bool, List[np.ndarray]]:
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
