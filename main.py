import pygame
import numpy as np

from constants import *
from game_objects import *

pygame.init()

WIN = pygame.display.set_mode(WIN_SIZE)


def draw(win, mass_points, springs, obstacles):
    win.fill("#192333")

    for spring in springs:
        spring.draw(win)

    for mass_point in mass_points:
        mass_point.draw(win)

    for obstacle in obstacles:
        obstacle.draw(win)

    pygame.display.update()


def main(win):
    mass_points = [
        MassPoint(np.array([300, 200]), 10),
        MassPoint(np.array([500, 400]), 10),
        MassPoint(np.array([500, 200]), 10),
        MassPoint(np.array([300, 400]), 10),
    ]

    springs = [
        Spring(mass_points[0:2], 100, 50, 6),
        Spring(mass_points[2:], 100, 50, 6),
        Spring((mass_points[0], mass_points[2]), 100, 50, 6),
        Spring((mass_points[1], mass_points[3]), 100, 50, 6),
        Spring((mass_points[1], mass_points[2]), 100, 50, 6),
        Spring((mass_points[0], mass_points[3]), 100, 50, 6),
    ]

    obstacles = [
        PolygonObstacle(np.array([(0, 600), (800, 550), (800, 600)])),
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
            mass_point.update(obstacles)

        draw(win, mass_points, springs, obstacles)

    pygame.quit()


if __name__ == "__main__":
    main(WIN)
