
import pygame
import numpy as np

from .game_object import GameObject
from .polygon_obstacle import PolygonObstacle
from softbody_simulation.consts import *
from softbody_simulation.utils import *


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
        self.pos = pos.astype(np.float64)
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
        self.selected = False

    def update(self, delta_time: float, obstacles=None, mass_points=None):
        if self.use_gravity:
            gravity_force = -np.array([0, 1]) * GRAVITY * self.mass  # gravity
            self.force += gravity_force

        damping_force = -self.damping * self.velocity
        self.force += damping_force

        self.velocity = self.force * delta_time / self.mass + self.velocity

        self.boundary_collision()
        # if mass_points:
        #     self.mass_point_collision(delta_time, mass_points)
        if obstacles:
            self.obstacle_collision(obstacles)

        self.pos = self.velocity * delta_time + self.pos

        self.force = 0

    def draw(self, win):
        win.blit(self.surface, self.pos - self.RADIUS)
        if self.selected:
            pygame.draw.circle(win, (255, 255, 0), tuple(self.pos), 12, 2)

    def mass_point_collision(self, delta_time, mass_points):
        for mass_point in mass_points:
            if ball_ball_collide(self, mass_point):
                line = np.array([self.pos, mass_point.pos])
                line_dir = line[0] - line[1]
                self.pos = line_dir * self.velocity * delta_time + self.pos

    def obstacle_collision(self, obstacles):
        for obstacle in obstacles:
            # if pixel_collide(self, obstacle):
            colliding_edge = obstacle.get_colliding_edge(self.pos, threshold=self.RADIUS)
            if colliding_edge:
                self.reflect(colliding_edge)

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
        p1, p2 = line
        edge_dir = p2 - p1

        norm = np.linalg.norm(edge_dir)
        if norm == 0:
            return
        normal = -np.array([-edge_dir[1], edge_dir[0]]) / norm

        dist = distance_point_to_line(self.pos, line)
        penetration = self.RADIUS - dist

        if penetration > 0:
            self.pos += normal * (penetration + 1e-3)

        v_dot_n = np.dot(self.velocity, normal)
        if v_dot_n < 0:
            self.velocity = self.velocity - 2 * v_dot_n * normal
            self.velocity *= self.BOUNCINESS
