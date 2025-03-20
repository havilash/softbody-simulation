import pygame
from typing import List, Optional
import numpy as np
from consts import WIN_SIZE
from softbody_simulation.entities import GameObject, MassPoint, Spring
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
        self.selected_mass_point: Optional[MassPoint] = None
        self.selected_spring: Optional[Spring] = None
        self.paused = False
        self.single_step = False

    # UI update functions
    def update_mass(self, value: float) -> None:
        self.default_mass = value
        if self.selected_mass_point:
            self.selected_mass_point.mass = value

    def update_stiffness(self, value: float) -> None:
        self.default_stiffness = value
        if self.selected_spring:
            self.selected_spring.stiffness = value

    def update_rest_length(self, value: float) -> None:
        self.default_rest_length = value
        if self.selected_spring:
            self.selected_spring.rest_length = value

    def update_damping(self, value: float) -> None:
        self.default_damping = value
        if self.selected_spring:
            self.selected_spring.damping = value

    def toggle_pause(self, screen: pygame.Surface) -> None:
        self.paused = not self.paused

    def perform_single_step(self, screen: pygame.Surface) -> None:
        if self.paused:
            self.single_step = True

    # Simulation input functions
    def handle_left_click(self, mouse_pos) -> None:
        mass_point = self._get_mass_point_at(mouse_pos)
        if mass_point:
            if self.selected_mass_point and self.selected_mass_point != mass_point:
                new_spring = Spring(
                    (self.selected_mass_point, mass_point),
                    stiffness=self.default_stiffness,
                    rest_length=self.default_rest_length,
                    damping=self.default_damping,
                )
                self.springs.append(new_spring)
                self.selected_mass_point = None
            else:
                self.selected_mass_point = mass_point
                self.selected_spring = None
        else:
            spring = self._get_spring_at(mouse_pos)
            if spring:
                self.selected_spring = spring
                self.selected_mass_point = None
            else:
                self.selected_mass_point = None
                self.selected_spring = None

    def handle_right_click(self, mouse_pos) -> None:
        new_point = MassPoint(np.array(mouse_pos), self.default_mass)
        self.mass_points.append(new_point)

    def handle_escape_keydown(self, key) -> None:
        self.selected_mass_point = None
        self.selected_spring = None

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
        for point in self.mass_points:
            point.update()
        for spring in self.springs:
            spring.update()
