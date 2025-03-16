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
    BOUNCINESS = 1

    def __init__(
        self,
        pos: np.ndarray,
        mass: float,
        velocity: np.ndarray = np.array([0, 0]),
        use_gravity=True,
    ):
        self.pos = pos
        self.inital_pos = pos
        self.velocity = velocity
        self.inital_velocity = velocity
        self.pvelocity = self.velocity
        self.mass = mass
        self.force = 0
        self.use_gravity = use_gravity

        self.surface = pygame.Surface(
            (self.RADIUS * 2, self.RADIUS * 2), pygame.SRCALPHA, 32
        )
        pygame.draw.circle(self.surface, RED, (self.RADIUS, self.RADIUS), self.RADIUS)

        self.mask = pygame.mask.from_surface(self.surface)
        self.rect = self.surface.get_rect()

    def update(self, obstacles=None, mass_points=None):

        if self.use_gravity:
            force_gravity = -np.array([0, 1]) * GRAVITY * self.mass  # gravity
            self.force += force_gravity

        self.velocity = self.force * self.deltatime / self.mass + self.velocity

        self.boundary_collision()
        # if mass_points:
        #     self.mass_point_collision(mass_points)
        if obstacles:
            self.obstacle_collision(obstacles)

        self.pos = self.velocity * self.deltatime + self.pos

        self.force = 0

    def draw(self, win):
        win.blit(self.surface, self.pos - self.RADIUS)

    def mass_point_collision(self, mass_points):
        for masspoint in mass_points:
            if ball_ball_collide(self, masspoint):
                line = np.array([self.pos, masspoint.pos])
                line_dir = line[0] - line[1]
                self.pos = line_dir * self.velocity * self.deltatime + self.pos

    def obstacle_collision(self, obstacles):
        for obstacle in obstacles:
            if pixel_collide(self, obstacle):
                if isinstance(obstacle, PolygonObstacle):
                    for i in range(len(obstacle.points) - 1):
                        line = obstacle.points[i], obstacle.points[i + 1]
                        if circle_line_distance(line, self.pos) <= self.RADIUS + 1:
                            self.reflect(line)

    def boundary_collision(self):
        if self.pos[0] - self.RADIUS <= 0:
            self.pos[0] = self.RADIUS
            self.velocity[0] = -self.velocity[0]
        elif self.pos[0] + self.RADIUS >= WIN_SIZE[0]:
            self.pos[0] = WIN_SIZE[0] - self.RADIUS
            self.velocity[0] = -self.velocity[0]

        if self.pos[1] - self.RADIUS <= 0:
            self.pos[1] = self.RADIUS
            self.velocity[1] = -self.velocity[1]
        elif self.pos[1] + self.RADIUS >= WIN_SIZE[1]:
            self.pos[1] = WIN_SIZE[1] - self.RADIUS
            self.velocity[1] = -self.velocity[1]

    def reflect(self, line):
        line_dir = line[1] - line[0]
        normal_vector = np.array((-line_dir[1], line_dir[0]))

        reflection_vector = to_pygame_vector(self.velocity).reflect(
            to_ndarray(normal_vector)
        )

        reflection_vector = np.array(list(reflection_vector))

        self.velocity = reflection_vector * self.BOUNCINESS


class Spring:
    def __init__(self, mass_points, stiffness, rest_length, damping_factor):
        self.a, self.b = mass_points
        self.stiffness = stiffness
        self.rest_length = rest_length
        self.damping_factor = damping_factor

    def update(self):
        self.force = 0

        force_s = -self.stiffness * (self.rest_length - abs(self.b.pos - self.a.pos))

        # direction_a = (self.b.pos - self.a.pos) / (np.linalg.norm(self.b.pos - self.a.pos) + tolerance)
        # direction_b = (self.a.pos - self.b.pos) / (np.linalg.norm(self.a.pos - self.b.pos) + tolerance)

        pos_delta = self.b.pos - self.a.pos
        pos_norm = np.linalg.norm(pos_delta)
        direction_a = pos_delta / pos_norm if pos_norm != 0 else np.zeros_like(pos_delta)
        direction_b = -direction_a

        velocity_diff = self.b.velocity - self.a.velocity
        force_d = direction_a * velocity_diff * self.damping_factor

        self.force += force_s + force_d

        self.a.force += self.force * direction_a
        self.b.force += self.force * direction_b

        # print("Spring Update Log:")
        # print(f"  Spring Force (force_s): {force_s}")
        # print(f"  Unit Direction A (direction_a): {direction_a}")
        # print(f"  Unit Direction B (direction_b): {direction_b}")
        # print(f"  Velocity Difference (velocity_diff): {velocity_diff}")
        # print(f"  Damping Force (force_d): {force_d}")
        # print(f"  Total Force (self.force): {self.force}")
        # print(f"  Mass Point A Total Force (self.a.force): {self.a.force}")
        # print(f"  Mass Point B Total Force (self.b.force): {self.b.force}")

    def draw(self, win):
        pygame.draw.line(win, WHITE, self.a.pos, self.b.pos)


class PolygonObstacle(GameObject):
    color = WHITE
    size = WIN_SIZE

    def __init__(self, points, color=color):
        self.pos = 0, 0
        self.points = points
        self.color = color

        self.surface = pygame.Surface(self.size, pygame.SRCALPHA)
        pygame.draw.polygon(self.surface, self.color, self.points)

        self.mask = pygame.mask.from_surface(self.surface)
        self.rect = self.surface.get_rect()

    def draw(self, win: pygame.Surface):
        win.blit(self.surface, self.pos)
