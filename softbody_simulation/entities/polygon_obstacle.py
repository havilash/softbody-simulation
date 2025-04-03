import pygame

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

    def contains_point(self, point, threshold=0):
        if len(self.points) < 3:
            return False

        inside = False
        n = len(self.points)

        tx, ty = point
        p1x, p1y = self.points[0]

        for i in range(1, n + 1):
            p2x, p2y = self.points[i % n]

            min_y, max_y = min(p1y, p2y) - threshold, max(p1y, p2y) + threshold
            max_x = max(p1x, p2x) + threshold

            if min_y < ty <= max_y and tx <= max_x:
                if p1y != p2y:  # Avoid division by zero
                    x_intersect = (ty - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
                    if p1x == p2x or tx <= x_intersect + threshold:
                        inside = not inside

            p1x, p1y = p2x, p2y

        return inside

    def near_boundary(self, point, threshold=5):
        if len(self.points) < 2:
            return False

        n = len(self.points)
        for i in range(n):
            p1 = self.points[i]
            p2 = self.points[(i + 1) % n]

            dist = distance_point_to_line(point, (p1, p2))
            if dist <= threshold:
                return True
        return False

    def get_colliding_edge(self, point, threshold):
        n = len(self.points)
        for i in range(n):
            p1 = self.points[i]
            p2 = self.points[(i + 1) % n]
            if distance_point_to_line(point, (p1, p2)) <= threshold:
                return (p1, p2)
        return None
