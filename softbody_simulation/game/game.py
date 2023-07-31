import pygame
import numpy as np

from constants import *
from utils import *
from game_objects import *

pygame.init()


def generate_objects(pos, size, spacing, mass_point_kwargs, spring_kwargs):
    diagonal_rest_length = math.sqrt(2 * spacing**2)
    mass_points = []
    for j in range(0, size[1] * spacing, spacing):
        for i in range(0, size[0] * spacing, spacing):
            mass_points.append(
                MassPoint(np.array([pos[0] + i, pos[1] + j]), **mass_point_kwargs)
            )
    springs = []
    for y in range(size[1]):
        for x in range(size[0]):
            i = lambda x, y: x + y * size[0]
            if x + 1 < size[0]:
                springs.append(
                    Spring(
                        (mass_points[i(x, y)], mass_points[i(x + 1, y)]), **spring_kwargs
                    )
                )
            if y + 1 < size[1]:
                springs.append(
                    Spring(
                        (mass_points[i(x, y)], mass_points[i(x, y + 1)]), **spring_kwargs
                    )
                )
            if x + 1 < size[0] and y + 1 < size[1]:
                springs.append(
                    Spring(
                        (mass_points[i(x, y)], mass_points[i(x + 1, y + 1)]),
                        **spring_kwargs
                    )
                )
            if x + 1 < size[0] and y + 1 < size[1]:
                springs.append(
                    Spring(
                        (mass_points[i(x + 1, y)], mass_points[i(x, y + 1)]),
                        **spring_kwargs
                    )
                )

    return mass_points, springs


def draw(win, mass_points, springs, obstacles):
    win.fill(BG_COLOR)

    for spring in springs:
        spring.draw(win)

    for mass_point in mass_points:
        mass_point.draw(win)

    for obstacle in obstacles:
        obstacle.draw(win)

    pygame.display.update()


def game(win):
    mass_points = [
        MassPoint(np.array([300, 200]), 10),
        MassPoint(np.array([500, 400]), 10),
        # MassPoint(np.array([500, 200]), 10),
        # MassPoint(np.array([300, 400]), 10),
    ]

    springs = [
        Spring(mass_points[0:2], 100, 50, 100),
        # Spring(mass_points[2:], 100, 50, 10),
        # Spring((mass_points[0], mass_points[2]), 100, 50, 10),
        # Spring((mass_points[1], mass_points[3]), 100, 50, 10),
        # Spring((mass_points[1], mass_points[2]), 100, 50, 10),
        # Spring((mass_points[0], mass_points[3]), 100, 50, 10),
    ]

    mass_points, springs = generate_objects(
        (100, 100),
        (2, 10),
        40,
        {"mass": 10},
        {"stiffness": 3000, "rest_length": 40, "damping_factor": 1},
    )

    obstacles = [
        # PolygonObstacle(np.array([(0, 600), (0, 600), (800, 550), (800, 600)])),
    ]

    run = True
    clock = pygame.time.Clock()
    while run:
        time_passed = clock.tick(FPS)
        fps = clock.get_fps()
        GameObject.set_deltatime(fps if fps > 0 else FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    run = False
                    break

        for spring in springs:
            spring.update()

        for mass_point in mass_points:
            mass_point.update(obstacles, [m for m in mass_points if m != mass_point])

        draw(win, mass_points, springs, obstacles)


if __name__ == "__main__":
    game(pygame.display.set_mode(WIN_SIZE))