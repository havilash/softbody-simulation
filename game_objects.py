import pygame
import numpy as np

from constants import *
from utils import *


class GameObject:
    deltatime = FPS

    @classmethod
    def set_deltatime(cls, fps):
        cls.deltatime = 1 / fps


class MassPoint(GameObject):
    RADIUS = 5

    def __init__(
        self,
        pos: np.ndarray,
        mass: float,
        velocity: np.ndarray = np.array([0, 0]),
    ):
        self.pos = pos
        self.inital_pos = pos
        self.velocity = velocity
        self.inital_velocity = velocity
        self.pvelocity = self.velocity
        self.force_spring = 0
        self.mass = mass

        self.surface = pygame.Surface(
            (self.RADIUS * 2, self.RADIUS * 2), pygame.SRCALPHA, 32
        )
        pygame.draw.circle(self.surface, RED, (self.RADIUS, self.RADIUS), self.RADIUS)

        self.mask = pygame.mask.from_surface(self.surface)
        self.rect = self.surface.get_rect()

    def update(self, obstacles=None):
        self.force = 0

        force_gravity = -np.array([0, 1]) * GRAVITY * self.mass  # gravity

        self.force += force_gravity
        self.force += self.force_spring  # spring

        self.velocity = self.force * self.deltatime / self.mass + self.velocity

        if obstacles:
            self.velocity = self.collision(self.velocity, obstacles)

        self.pos = 0.9 * self.velocity * self.deltatime + self.pos

        self.force_spring = 0

    def draw(self, win):
        win.blit(self.surface, self.pos - self.RADIUS)

    def collision(self, inital_velocity, obstacles):
        for o in obstacles:
            if isinstance(o, PolygonObstacle):
                for i in range(0, len(o.points) - 1):
                    line = o.points[i], o.points[i + 1]
                    if circle_line_distance(line, self.pos) <= self.RADIUS:
                        line_dir = (line[1] - line[0]) / abs(line[1] - line[0])
                        normal_vector = np.array(line_dir[1], line_dir[0])

                        reflection_vector = (
                            inital_velocity
                            - 2
                            * np.sum(inital_velocity * normal_vector)
                            * normal_vector
                        )
                        print(inital_velocity)
                        print(reflection_vector)

                        return reflection_vector

        return inital_velocity


class Spring:
    def __init__(self, mass_points, stiffness, rest_length, damping_factor):
        self.a, self.b = mass_points
        self.stiffness = stiffness
        self.rest_length = rest_length
        self.damping_factor = damping_factor

    def update(self):
        self.force = 0
        force_s = self.stiffness * (abs(self.b.pos - self.a.pos) - self.rest_length)

        direction_a = (self.b.pos - self.a.pos) / np.maximum(
            abs(self.b.pos - self.a.pos), 1
        )
        direction_b = (self.a.pos - self.b.pos) / np.maximum(
            abs(self.a.pos - self.b.pos), 1
        )
        velocity_diff = self.b.velocity - self.a.velocity
        force_d = direction_a * velocity_diff * self.damping_factor

        self.force = force_s + force_d

        self.a.force_spring += self.force * direction_a
        self.b.force_spring += self.force * direction_b

        # print(
        #     f"force: {self.force}, a: {self.a.pos}, b: {self.b.pos}, av: {self.a.velocity}, bv: {self.b.velocity}"
        # )

    def draw(self, win):
        pygame.draw.line(win, WHITE, self.a.pos, self.b.pos)


class Obstacle(GameObject):
    color = WHITE

    def __init__(self, pos, size, color=color, angle=0):
        self.pos = pos
        self.size = size
        self.color = color

        self.surface = pygame.Surface(self.size, pygame.SRCALPHA)
        self.surface.fill(self.color)
        self.surface = pygame.transform.rotate(self.surface, angle)

        self.mask = pygame.mask.from_surface(self.surface)
        self.rect = self.surface.get_rect()

    def draw(self, win: pygame.Surface):
        win.blit(self.surface, self.pos)


class PolygonObstacle(GameObject):
    color = WHITE
    size = WIN_SIZE

    def __init__(self, points, color=color):
        self.points = points
        self.color = color

        self.surface = pygame.Surface(self.size, pygame.SRCALPHA)
        pygame.draw.polygon(self.surface, self.color, self.points)

        self.mask = pygame.mask.from_surface(self.surface)
        self.rect = self.surface.get_rect()

    def draw(self, win: pygame.Surface):
        win.blit(self.surface, (0, 0))
