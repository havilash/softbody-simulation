import pygame
import numpy as np

from .game_object import GameObject
from softbody_simulation.consts import *
from softbody_simulation.utils import *


class Spring(GameObject):
    def __init__(self, mass_points, stiffness, damping, rest_length=None):
        self.a, self.b = mass_points
        self.stiffness = stiffness
        self.rest_length = rest_length or np.linalg.norm(self.a.pos - self.b.pos)
        self.damping = damping
        self.selected = False

    def update(self, delta_time: float):
        pos_delta = self.b.pos - self.a.pos
        pos_norm = np.linalg.norm(pos_delta)

        direction = pos_delta / pos_norm if pos_norm != 0 else np.zeros_like(pos_delta)

        spring_force = -self.stiffness * (self.rest_length - pos_norm) * direction

        velocity_diff = self.b.velocity - self.a.velocity
        proj = np.dot(velocity_diff, direction)

        damping_force = self.damping * proj * direction

        total_force = spring_force + damping_force

        self.a.force += total_force
        self.b.force -= total_force

    def draw(self, screen):
        pygame.draw.line(screen, WHITE, self.a.pos, self.b.pos)

        if self.selected:
            pygame.draw.line(screen, (255, 255, 0), self.a.pos, self.b.pos, 4)

