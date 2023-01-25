import pygame
import math
import numpy as np

from game_objects import *


def distance(p1, p2):
    d = p2 - p1
    return math.sqrt(np.sum(d**2))


def pixel_collide(obj1, obj2):
    offset = obj2.pos - obj1.pos
    poi = obj1.mask.overlap(obj2.mask, offset)  # point of intercept

    if poi:
        return poi
    return False


def circle_line_distance(line, pos):
    dist = 2 * triangle_area(*line, pos) / distance(line[0], line[1])
    return dist


def triangle_area(a, b, c):
    ab = b - a
    ac = c - a
    cross_product = ab[0] * ac[1] - ab[1] * ac[0]
    return abs(cross_product) / 2
