import pygame
import numpy as np
from scenes.scene_manager import Scene, get_scene_manager
from consts import (
    TRANSPARENT_COLOR,
    TRANSPARENT_HOVER_COLOR,
    WIN_SIZE,
    BG_COLOR,
    FPS,
    FONT,
    FONT_COLOR,
)
import pygame_ui as ui
from softbody_simulation.scripts.simulation import SimulationScript


class SimulationScene(Scene):
    def __init__(self, screen: pygame.Surface):
        super().__init__(screen)
        self.screen = screen

        self.script = SimulationScript()

        self.back_button = ui.Button(
            (10, 10),
            (100, 40),
            text="Back",
            font=FONT,
            font_color=FONT_COLOR,
            color=TRANSPARENT_COLOR,
            hover_color=TRANSPARENT_HOVER_COLOR,
            func=self.go_back,
        )

    def go_back(self, screen: pygame.Surface):
        from scenes.main_menu import MainMenu

        get_scene_manager().switch_scene(MainMenu(self.screen))

    def handle_events(self) -> bool:
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                return False

            mouse_pos = pygame.mouse.get_pos()
            if (
                self.back_button.is_over(mouse_pos)
                and event.type == pygame.MOUSEBUTTONDOWN
            ):
                self.back_button.call_back(self.screen)

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False

            self.script.process_event(event)
        return True

    def update(self) -> None:
        self.script.update()

    def render(self) -> None:
        self.screen.fill(BG_COLOR)
        for spring in self.script.springs:
            spring.draw(self.screen)
        for mass_point in self.script.mass_points:
            mass_point.draw(self.screen)
        for obstacle in self.script.obstacles:
            obstacle.draw(self.screen)

        self.back_button.draw(self.screen)
        pygame.display.update()
