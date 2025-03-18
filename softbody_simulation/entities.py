import pygame
import numpy as np

from softbody_simulation.consts import *
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
        damping=0,
    ):
        self.pos = pos
        self.initial_pos = pos
        self.velocity = velocity
        self.initial_velocity = velocity
        self.previous_velocity = self.velocity
        self.mass = mass
        self.force = 0
        self.use_gravity = use_gravity
        self.damping = damping

        self.surface = pygame.Surface(
            (self.RADIUS * 2, self.RADIUS * 2), pygame.SRCALPHA, 32
        )
        pygame.draw.circle(self.surface, RED, (self.RADIUS, self.RADIUS), self.RADIUS)

        self.mask = pygame.mask.from_surface(self.surface)
        self.rect = self.surface.get_rect()

    def update(self, obstacles=None, mass_points=None):

        if self.use_gravity:
            gravity_force = -np.array([0, 1]) * GRAVITY * self.mass  # gravity
            self.force += gravity_force

        damping_force = -self.damping * self.velocity
        self.force += damping_force

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
        for mass_point in mass_points:
            if ball_ball_collide(self, mass_point):
                line = np.array([self.pos, mass_point.pos])
                line_dir = line[0] - line[1]
                self.pos = line_dir * self.velocity * self.deltatime + self.pos

    def obstacle_collision(self, obstacles):
        for obstacle in obstacles:
            if pixel_collide(self, obstacle):
                if isinstance(obstacle, PolygonObstacle):
                    for i in range(len(obstacle.points) - 1):
                        line = obstacle.points[i], obstacle.points[i + 1]
                        if distance_point_to_line(self.pos, line) <= self.RADIUS + 1:
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
    def __init__(self, mass_points, stiffness, damping, rest_length=None):
        self.a, self.b = mass_points
        self.stiffness = stiffness
        self.rest_length = rest_length or np.linalg.norm(self.a.pos - self.b.pos)
        self.damping = damping

    def update(self):
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
