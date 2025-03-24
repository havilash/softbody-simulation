import pygame
import numpy as np

from .game_object import GameObject
from softbody_simulation.consts import *
from softbody_simulation.utils import *


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
        self.selected = False

    def draw(self, win: pygame.Surface):
        win.blit(self.surface, self.pos)

        if self.selected:
            if len(self.points) > 0:
                tuple_points = [tuple(v) for v in self.points]
                pygame.draw.lines(win, (255, 255, 0), True, tuple_points, 3)
                for point in tuple_points:
                    pygame.draw.circle(win, (255, 255, 0), point, 5)

    def contains_point(self, point):
        """
        Check if a point is inside the polygon using ray casting algorithm.
        """
        if len(self.points) < 3:
            return False

        inside = False
        n = len(self.points)

        p1x, p1y = self.points[0]
        for i in range(n + 1):
            p2x, p2y = self.points[i % n]

            if point[1] > min(p1y, p2y):
                if point[1] <= max(p1y, p2y):
                    if point[0] <= max(p1x, p2x):
                        if p1y != p2y:
                            x_intersect = (point[1] - p1y) * (p2x - p1x) / (
                                p2y - p1y
                            ) + p1x
                        if p1x == p2x or point[0] <= x_intersect:
                            inside = not inside
            p1x, p1y = p2x, p2y

        return inside

    def near_boundary(self, point, threshold=5):
        """
        Check if a point is near the boundary of the polygon.
        """
        if len(self.points) < 2:
            return False

        n = len(self.points)

        for i in range(n):
            p1 = self.points[i]
            p2 = self.points[(i + 1) % n]

            # Calculate distance from point to line segment
            dist = distance_point_to_line(point, (p1, p2))

            if dist <= threshold:
                return True

        return False
