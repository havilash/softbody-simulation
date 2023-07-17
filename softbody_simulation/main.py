import math
import os.path
import sys
import pygame
import numpy as np

from constants import *
from utils import *
from game_objects import *
import pygame_ui as ui
import game


def draw(win: pygame.Surface, buttons, texts):
    win.fill(BG_COLOR)

    for button in buttons:
        button.draw(win)

    for text in texts:
        text.draw(win)

    pygame.display.update()


def main_menu():
    win = pygame.display.set_mode(WIN_SIZE)
    pygame.display.set_caption("Spring Simulation")

    texts = [
        ui.Text(
            (WIN_SIZE[0] / 2, WIN_SIZE[1] / 4),
            "Spring Simulation",
            75,
            font=FONT,
            color=FONT_COLOR,
        )
    ]

    buttons = {
        "start": ui.Button(
            (WIN_SIZE[0] / 2 - 200 / 2, WIN_SIZE[1] / 2 - 50 / 2),
            (200, 50),
            text="Start",
            font=FONT,
            font_color=FONT_COLOR,
            color="#0a5c9e",
            hover_color="#0d7eff",
            func=game.game,
        ),
        "cursor": ui.Button(
            (WIN_SIZE[0] / 2 - 200 / 2, WIN_SIZE[1] / 2 + 50),
            (200, 50),
            text="Cursor",
            font=FONT,
            font_color=FONT_COLOR,
            color="#0a5c9e",
            hover_color="#0d7eff",
            func=game.cursor_game,
        ),
    }

    is_running = True
    clock = pygame.time.Clock()

    while is_running:
        time_passed = clock.tick(FPS)
        mpos = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                is_running = False
                break
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    is_running = False
                    break

                if event.key == pygame.K_RETURN:
                    buttons["start"].call_back(win)

            for button in buttons.values():
                if button.is_over(mpos):
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        if button in [buttons[x] for x in ("start", "cursor")]:
                            button.call_back(win)

        draw(win, buttons.values(), texts)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main_menu()
