import pygame
import math
import numpy as np



def distance(p1, p2):
    d = p2 - p1
    return math.sqrt(np.sum(d**2))


def pixel_collide(obj1, obj2):
    offset = obj2.pos - obj1.pos
    poi = obj1.mask.overlap(obj2.mask, offset)  # point of intercept

    if poi:
        return poi
    return False


def ball_ball_collide(obj1, obj2):
    return distance(obj1.pos, obj2.pos) <= obj1.RADIUS + obj2.RADIUS


def to_ndarray(vector: pygame.math.Vector2):
    return np.array(list(vector))


def to_pygame_vector(vector: np.ndarray):
    return pygame.math.Vector2(list(vector))


def distance_point_to_line(
    point: np.ndarray, line: tuple[np.ndarray, np.ndarray]
) -> float:
    start, end = line
    if np.array_equal(start, end):
        return float(np.linalg.norm(point - start))
    t = np.dot(point - start, end - start) / np.dot(end - start, end - start)
    t = max(0, min(1, t))
    projection = start + t * (end - start)
    return float(np.linalg.norm(point - projection))


class Singleton:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)  # Fix: No extra arguments
        return cls._instance
