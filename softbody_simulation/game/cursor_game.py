import pygame
import numpy as np

from constants import *
from game_objects import *
import pygame_ui as ui

pygame.init()


def draw(win, cursor_mass_point, mass_point, spring, ui_elements):
    win.fill(BG_COLOR)

    # ui
    rect = pygame.Rect(WIN_SIZE[0] - 160, 10, 150, 200)
    pygame.draw.rect(win, "#0a5c9e", rect)
    for ui_element in ui_elements:
        ui_element.draw(win)

    spring.draw(win)
    cursor_mass_point.draw(win)
    mass_point.draw(win)

    pygame.display.update()


def cursor_game(win):
    mass_point = MassPoint(np.array([300, 200]), 100)
    cursor_mass_point = MassPoint(np.array([300, 300]), float("inf"))
    spring = Spring((cursor_mass_point, mass_point), 100, 50, 10)

    # UI
    sliders = {
        "stiffness": ui.Slider(
            (WIN_SIZE[0] - 135, 40), (100, 5), vrange=(0, 300), value=spring.stiffness
        ),
        "rest_length": ui.Slider(
            (WIN_SIZE[0] - 135, 80),
            (100, 5),
            vrange=(0, 300),
            value=spring.rest_length + 100000,
        ),
        "damping_factor": ui.Slider(
            (WIN_SIZE[0] - 135, 120),
            (100, 5),
            vrange=(0, 100),
            value=spring.damping_factor + 10000,
        ),
        "mass": ui.Slider(
            (WIN_SIZE[0] - 135, 160), (100, 5), vrange=(1, 200), value=mass_point.mass
        ),
    }
    texts = [
        ui.Text((WIN_SIZE[0] - 85, 25), "Stiffness", size=20),
        ui.Text((WIN_SIZE[0] - 85, 65), "Rest Length", size=20),
        ui.Text((WIN_SIZE[0] - 85, 105), "Damping Factor", size=20),
        ui.Text((WIN_SIZE[0] - 85, 145), "Mass", size=20),
    ]

    ui_elements = [*sliders.values(), *texts]

    run = True
    clock = pygame.time.Clock()
    while run:
        time_passed = clock.tick(FPS)
        mpos = pygame.mouse.get_pos()
        fps = clock.get_fps()
        GameObject.set_deltatime(fps if fps > 0 else FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    run = False
                    break

            if pygame.mouse.get_pressed()[0]:  # right click
                cursor_mass_point.pos = np.array(mpos)

            if pygame.mouse.get_pressed()[2]:  # left click
                for slider in sliders.values():
                    if slider.is_over(mpos):
                        slider.update(mpos[0])
                        if slider == sliders["stiffness"]:
                            spring.stiffness = slider.get_value()
                        if slider == sliders["rest_length"]:
                            spring.rest_length = slider.get_value()
                        if slider == sliders["damping_factor"]:
                            spring.damping_factor = slider.get_value()
                        if slider == sliders["mass"]:
                            mass_point.mass = slider.get_value()

        spring.update()

        mass_point.update()

        draw(win, cursor_mass_point, mass_point, spring, ui_elements)


if __name__ == "__main__":
    cursor_game(pygame.display.set_mode(WIN_SIZE))
