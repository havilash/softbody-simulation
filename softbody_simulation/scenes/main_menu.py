import pygame
from scenes.scene_manager import Scene, get_scene_manager
from consts import WIN_SIZE, BG_COLOR, FONT, FONT_COLOR
import pygame_ui as ui
from scenes.sandbox import SandboxScene
from scenes.simulation import SimulationScene


class MainMenu(Scene):
    def __init__(self, screen: pygame.Surface):
        super().__init__(screen)
        self.title = ui.Text(
            (WIN_SIZE[0] / 2, WIN_SIZE[1] / 4),
            "Spring Simulation",
            75,
            font=FONT,
            color=FONT_COLOR,
        )
        self.start_button = ui.Button(
            (WIN_SIZE[0] // 2 - 100, WIN_SIZE[1] // 2 - 25),
            (200, 50),
            text="Start",
            font=FONT,
            font_color=FONT_COLOR,
            color="#0a5c9e",
            hover_color="#0d7eff",
            func=self.go_to_simulation,
        )
        self.sandbox_button = ui.Button(
            (WIN_SIZE[0] // 2 - 100, WIN_SIZE[1] // 2 + 50),
            (200, 50),
            text="Sandbox",
            font=FONT,
            font_color=FONT_COLOR,
            color="#0a5c9e",
            hover_color="#0d7eff",
            func=self.go_to_sandbox,
        )

    def go_to_simulation(self, _screen: pygame.Surface):
        get_scene_manager().switch_scene(SimulationScene(self.screen))

    def go_to_sandbox(self, _screen: pygame.Surface):
        get_scene_manager().switch_scene(SandboxScene(self.screen))

    def handle_events(self) -> bool:
        for event in pygame.event.get():
            mouse_pos = pygame.mouse.get_pos()
            if (
                self.start_button.is_over(mouse_pos)
                and event.type == pygame.MOUSEBUTTONDOWN
            ):
                self.start_button.call_back(self.screen)
            elif (
                self.sandbox_button.is_over(mouse_pos)
                and event.type == pygame.MOUSEBUTTONDOWN
            ):
                self.sandbox_button.call_back(self.screen)

            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False
                if event.key == pygame.K_RETURN:
                    self.go_to_simulation(self.screen)

        return True

    def update(self) -> None:
        pass

    def render(self) -> None:
        self.screen.fill(BG_COLOR)
        self.start_button.draw(self.screen)
        self.sandbox_button.draw(self.screen)
        self.title.draw(self.screen)
        pygame.display.update()
