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


def circle_line_distance(line, pos):
    dist = 2 * triangle_area(*line, pos) / distance(line[0], line[1])
    return dist


def triangle_area(a, b, c):
    ab = b - a
    ac = c - a
    cross_product = ab[0] * ac[1] - ab[1] * ac[0]
    return abs(cross_product) / 2


def to_ndarray(vector: pygame.math.Vector2):
    return np.array(list(vector))


def to_pygame_vector(vector: np.ndarray):
    return pygame.math.Vector2(list(vector))
