import pygame
from softbody_simulation.scenes.scene import UIScene
from softbody_simulation.consts import WIN_SIZE, BG_COLOR, FONT, FONT_COLOR
from softbody_simulation.scenes.sandbox import Sandbox
from softbody_simulation.scenes.simulation import Simulation
from softbody_simulation.scenes.scene_manager import SceneManager
from softbody_simulation.ui import Button, Text


class MainMenu(UIScene):
    def __init__(self, screen: pygame.Surface):
        super().__init__(screen, background_color=BG_COLOR)

        self.title = Text(
            center_pos=(WIN_SIZE[0] / 2, WIN_SIZE[1] / 4),
            text="Spring Simulation",
            size=75,
            font=FONT,
            color=FONT_COLOR,
        )
        self.add_ui_element(self.title)

        self.start_button = Button(
            pos=(WIN_SIZE[0] // 2 - 100, WIN_SIZE[1] // 2 - 25),
            size=(200, 50),
            text="Start",
            font=FONT,
            font_size=30,
            font_color=FONT_COLOR,
            color="#0a5c9e",
            hover_color="#0d7eff",
            callback=self.go_to_simulation,
        )
        self.add_ui_element(self.start_button)

        self.sandbox_button = Button(
            pos=(WIN_SIZE[0] // 2 - 100, WIN_SIZE[1] // 2 + 50),
            size=(200, 50),
            text="Sandbox",
            font=FONT,
            font_size=30,
            font_color=FONT_COLOR,
            color="#0a5c9e",
            hover_color="#0d7eff",
            callback=self.go_to_sandbox,
        )
        self.add_ui_element(self.sandbox_button)

    def go_to_simulation(self):
        SceneManager().switch_scene(Simulation(self.screen))

    def go_to_sandbox(self):
        SceneManager().switch_scene(Sandbox(self.screen))

    def handle_events(self) -> bool:
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                return False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False
                if event.key == pygame.K_RETURN:
                    self.go_to_simulation()

            for element in self.ui_elements:
                element.handle_event(event)
        return True

    def update(self, delta_time: float) -> None:
        for element in self.ui_elements:
            element.update()

    def render(self) -> None:
        self.screen.fill(BG_COLOR)
        for element in self.ui_elements:
            element.draw(self.screen)
        pygame.display.update()
