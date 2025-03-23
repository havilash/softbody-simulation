import pygame
from consts import (
    BG_COLOR,
    TRANSPARENT_COLOR,
    TRANSPARENT_HOVER_COLOR,
    FONT,
    FONT_COLOR,
)
from softbody_simulation.scenes.scene import UIScene
from softbody_simulation.scenes.scene_manager import SceneManager
from softbody_simulation.scripts.simulation import SimulationScript
from softbody_simulation.ui_elements.ui_button import UIButton


class SimulationScene(UIScene):
    def __init__(self, screen: pygame.Surface):
        super().__init__(screen, background_color=BG_COLOR)

        self.script = SimulationScript()

        back_button = UIButton(
            pos=(10, 10),
            size=(100, 40),
            text="Back",
            font=FONT,
            font_size=20,
            font_color=FONT_COLOR,
            color=TRANSPARENT_COLOR,
            hover_color=TRANSPARENT_HOVER_COLOR,
            callback=self.go_back,
        )
        self.add_ui_element(back_button)

    def go_back(self):
        from scenes.main_menu import MainMenuScene

        SceneManager().switch_scene(MainMenuScene(self.screen))

    def handle_events(self) -> bool:
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                return False

            for element in self.ui_elements:
                element.handle_event(event)

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False

        return True

    def update(self, delta_time: float) -> None:
        self.script.update(delta_time)

        for element in self.ui_elements:
            element.update()

    def render(self) -> None:
        self.screen.fill(BG_COLOR)

        for spring in self.script.springs:
            spring.draw(self.screen)
        for mass_point in self.script.mass_points:
            mass_point.draw(self.screen)
        for obstacle in self.script.obstacles:
            obstacle.draw(self.screen)

        for element in self.ui_elements:
            element.draw(self.screen)
        pygame.display.update()
