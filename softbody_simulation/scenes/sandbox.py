import pygame
from scenes.scene_manager import Scene, get_scene_manager
from consts import (
    FONT,
    FONT_COLOR,
    BG_COLOR,
    TRANSPARENT_COLOR,
    TRANSPARENT_HOVER_COLOR,
    WIN_SIZE,
)
import pygame_ui as ui
from softbody_simulation.scripts.sandbox import SandboxScript


class SandboxScene(Scene):
    def __init__(self, screen: pygame.Surface):
        super().__init__(screen)
        self.screen = screen

        self.script = SandboxScript(
            default_mass=100,
            default_stiffness=100,
            default_rest_length=50,
            default_damping=10,
        )

        self.ui_panel = pygame.Rect(WIN_SIZE[0] - 160, 10, 150, 300)

        mass_slider, mass_label = self._create_slider_with_label(
            text="Mass",
            slider_pos=(WIN_SIZE[0] - 135, 40),
            label_pos=(WIN_SIZE[0] - 85, 25),
            value_range=(1, 200),
            initial_value=self.script.default_mass,
            func=self.script.update_mass,
        )
        stiffness_slider, stiffness_label = self._create_slider_with_label(
            text="Stiffness",
            slider_pos=(WIN_SIZE[0] - 135, 80),
            label_pos=(WIN_SIZE[0] - 85, 65),
            value_range=(0, 300),
            initial_value=self.script.default_stiffness,
            func=self.script.update_stiffness,
        )
        rest_length_slider, rest_length_label = self._create_slider_with_label(
            text="Rest Length",
            slider_pos=(WIN_SIZE[0] - 135, 120),
            label_pos=(WIN_SIZE[0] - 85, 105),
            value_range=(0, 300),
            initial_value=self.script.default_rest_length,
            func=self.script.update_rest_length,
        )
        damping_slider, damping_label = self._create_slider_with_label(
            text="Damping",
            slider_pos=(WIN_SIZE[0] - 135, 160),
            label_pos=(WIN_SIZE[0] - 85, 145),
            value_range=(0, 100),
            initial_value=self.script.default_damping,
            func=self.script.update_damping,
        )

        self.sliders = [
            mass_slider,
            stiffness_slider,
            rest_length_slider,
            damping_slider,
        ]
        self.labels = [mass_label, stiffness_label, rest_length_label, damping_label]

        pause_button = self._create_button(
            pos=(WIN_SIZE[0] - 140, 220),
            size=(120, 30),
            text="Pause",
            func=self.script.toggle_pause,
        )
        step_button = self._create_button(
            pos=(WIN_SIZE[0] - 140, 260),
            size=(120, 30),
            text="Step",
            func=self.script.perform_single_step,
        )
        self.buttons = [pause_button, step_button]

        self.back_button = self._create_button(
            pos=(10, 10),
            size=(100, 40),
            text="Back",
            func=self.go_back,
            color=TRANSPARENT_COLOR,
            hover_color=TRANSPARENT_HOVER_COLOR,
        )

    def _create_slider_with_label(
        self,
        text,
        slider_pos,
        label_pos,
        value_range,
        initial_value,
        func,
    ):
        slider = ui.Slider(
            slider_pos, (100, 5), vrange=value_range, value=initial_value, func=func
        )
        label = ui.Text(label_pos, text, size=20)
        return slider, label

    def _create_button(
        self,
        pos,
        size,
        text,
        func,
        color="#0a5c9e",
        hover_color="#0d7eff",
    ):
        return ui.Button(
            pos,
            size,
            text=text,
            font=FONT,
            font_color=FONT_COLOR,
            color=color,
            hover_color=hover_color,
            func=func,
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
                continue

            if event.type == pygame.MOUSEBUTTONDOWN:
                if self._is_in_ui_panel(mouse_pos):
                    for button in self.buttons:
                        if button.is_over(mouse_pos):
                            button.call_back(self.screen)
                    for slider in self.sliders:
                        if slider.is_over(mouse_pos):
                            slider.update(mouse_pos[0])
                            slider.call_back(slider.value)
                else:
                    self.script.process_event(event)
        return True

    def _is_in_ui_panel(self, pos):
        return pos[0] > WIN_SIZE[0] - self.ui_panel.width

    def update(self) -> None:
        self.script.update()

    def render(self) -> None:
        self.screen.fill(BG_COLOR)

        # Sandbox
        for spring in self.script.springs:
            spring.draw(self.screen)
            if spring == self.script.selected_spring:
                p1, p2 = spring.mass_points[0].pos, spring.mass_points[1].pos
                pygame.draw.line(self.screen, (255, 255, 0), p1, p2, 4)
        for point in self.script.mass_points:
            point.draw(self.screen)
            if point == self.script.selected_mass_point:
                pygame.draw.circle(
                    self.screen, (255, 255, 0), point.pos.astype(int), 15, 2
                )

        # UI
        pygame.draw.rect(self.screen, "#0a5c9e", self.ui_panel)
        for element in self.sliders + self.labels + self.buttons:
            element.draw(self.screen)

        self.back_button.draw(self.screen)
        pygame.display.update()
