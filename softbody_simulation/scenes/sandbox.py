import pygame
from consts import (
    BG_COLOR,
    WIN_SIZE,
    FONT,
    FONT_COLOR,
    TRANSPARENT_COLOR,
    TRANSPARENT_HOVER_COLOR,
)
from softbody_simulation.scenes.scene import UIScene, get_scene_manager
from softbody_simulation.scripts.sandbox import SandboxScript
from softbody_simulation.ui_elements.ui_button import UIButton
from softbody_simulation.ui_elements.ui_slider import UISlider
from softbody_simulation.ui_elements.ui_text import UIText


def create_slider_with_label(label_text, pos, vrange, value, callback):
    label = UIText(center_pos=(pos[0], pos[1]), text=label_text, size=20)
    slider = UISlider(
        pos=(pos[0] - 50, pos[1] + 20),
        size=(100, 5),
        vrange=vrange,
        value=value,
        callback=callback,
    )
    return label, slider


class SandboxScene(UIScene):
    def __init__(self, screen: pygame.Surface):
        super().__init__(screen, background_color=BG_COLOR)
        self.script = SandboxScript(
            default_mass=100,
            default_stiffness=100,
            default_rest_length=50,
            default_damping=10,
        )

        self.back_button = UIButton(
            pos=(10, 10),
            size=(100, 40),
            text="Back",
            font=FONT,
            font_size=20,
            font_color=FONT_COLOR,
            color=TRANSPARENT_COLOR,
            hover_color=TRANSPARENT_HOVER_COLOR,
            callback=lambda: get_scene_manager().switch_scene(
                __import__("scenes.main_menu", fromlist=["MainMenu"]).MainMenu(
                    self.screen
                )
            ),
        )
        self.static_ui_elements = [self.back_button]

        self.current_ui_group = "all"
        self.dynamic_elements = self.build_dynamic_elements(self.current_ui_group)
        self.ui_elements = self.static_ui_elements + self.dynamic_elements

    def build_dynamic_elements(self, group: str):
        elements = []

        ui_panel_pos = WIN_SIZE[0] - 160, 10
        ui_panel_width = 150

        base_x, base_y, gap = (
            ui_panel_pos[0] + ui_panel_width / 2,
            ui_panel_pos[1] + 20,
            50,
        )

        ui_configs = {
            "mass": [
                (
                    "Mass",
                    (1, 200),
                    (
                        self.script.selected_mass_point.mass
                        if self.script.selected_mass_point
                        else self.script.default_mass
                    ),
                    self.script.update_mass,
                ),
            ],
            "spring": [
                (
                    "Stiffness",
                    (0, 300),
                    (
                        self.script.selected_spring.stiffness
                        if self.script.selected_spring
                        else self.script.default_stiffness
                    ),
                    self.script.update_stiffness,
                ),
                (
                    "Rest Length",
                    (0, 300),
                    (
                        self.script.selected_spring.stiffness
                        if self.script.selected_spring
                        else self.script.default_stiffness
                    ),
                    self.script.update_rest_length,
                ),
                (
                    "Damping",
                    (0, 100),
                    (
                        self.script.selected_spring.stiffness
                        if self.script.selected_spring
                        else self.script.default_stiffness
                    ),
                    self.script.update_damping,
                ),
            ],
        }

        selected_ui = []
        if group == "all":
            selected_ui = ui_configs["mass"] + ui_configs["spring"]
        elif group in ui_configs:
            selected_ui = ui_configs[group]

        ui_panel_height = (7 + gap) * len(selected_ui)
        self.ui_panel = pygame.Rect(*ui_panel_pos, ui_panel_width, ui_panel_height)

        for i, (label, vrange, value, callback) in enumerate(selected_ui):
            label_ui, slider_ui = create_slider_with_label(
                label, (base_x, base_y + gap * i), vrange, value, callback
            )
            elements.extend([label_ui, slider_ui])

        return elements

    def _is_in_ui_panel(self, pos):
        return pos[0] > WIN_SIZE[0] - self.ui_panel.width

    def handle_events(self) -> bool:
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                return False

            # Dispatch events to UI elements.
            for element in self.ui_elements:
                element.handle_event(event)

            if event.type == pygame.MOUSEBUTTONDOWN:
                if not self._is_in_ui_panel(event.pos):
                    if event.button == 1:
                        self.script.handle_left_click(event.pos)
                    elif event.button == 3:
                        self.script.handle_right_click(event.pos)
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.script.handle_escape_keydown(event.key)
                elif event.key == pygame.K_SPACE:
                    self.script.toggle_pause(event.key)
                elif event.key == pygame.K_RIGHT:
                    self.script.perform_single_step(event.key)
        return True

    def update(self, delta_time) -> None:
        self.script.update(delta_time)
        for element in self.ui_elements:
            element.update()

        desired_group = "all"
        if self.script.selected_spring is not None:
            desired_group = "spring"
        elif self.script.selected_mass_point is not None:
            desired_group = "mass"

        if desired_group != self.current_ui_group:
            self.current_ui_group = desired_group
            self.dynamic_elements = self.build_dynamic_elements(desired_group)
            self.ui_elements = self.static_ui_elements + self.dynamic_elements

    def render(self) -> None:
        self.screen.fill(BG_COLOR)

        for spring in self.script.springs:
            spring.draw(self.screen)
            if spring == self.script.selected_spring:
                p1, p2 = spring.a.pos, spring.b.pos
                pygame.draw.line(self.screen, (255, 255, 0), p1, p2, 4)
        for point in self.script.mass_points:
            point.draw(self.screen)
            if point == self.script.selected_mass_point:
                pygame.draw.circle(
                    self.screen, (255, 255, 0), point.pos.astype(int), 15, 2
                )

        pygame.draw.rect(self.screen, "#0a5c9e", self.ui_panel)

        for element in self.ui_elements:
            element.draw(self.screen)
        pygame.display.update()
