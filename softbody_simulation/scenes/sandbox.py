import pygame
from softbody_simulation.consts import (
    BG_COLOR,
    WIN_SIZE,
    FONT,
    FONT_COLOR,
    TRANSPARENT_COLOR,
    TRANSPARENT_HOVER_COLOR,
)
import numpy as np
from softbody_simulation.scenes.scene import UIScene
from softbody_simulation.scenes.scene_manager import SceneManager
from softbody_simulation.scripts.sandbox import Sandbox as SandboxScript, Mode
from softbody_simulation.ui import Button, SandboxPanel

class Sandbox(UIScene):
    def __init__(self, screen: pygame.Surface):
        super().__init__(screen, background_color=BG_COLOR)
        self.script = SandboxScript(
            default_mass=100,
            default_stiffness=100,
            default_rest_length=50,
            default_damping=10,
        )

        # Create back button
        self.back_button = Button(
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

        self.ui_panel = SandboxPanel(
            script=self.script,
        )
        
        self.ui_elements = [self.back_button, self.ui_panel]

        self.last_click_time = 0

    def go_back(self):
        from softbody_simulation.scenes.main_menu import MainMenu
        SceneManager().switch_scene(MainMenu(self.screen))

    def _is_in_ui_panel(self, pos):
        return self.ui_panel.contains_point(pos)

    def handle_events(self) -> bool:
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                return False

            for element in self.ui_elements:
                element.handle_event(event)

            if event.type == pygame.MOUSEBUTTONDOWN:
                current_time = pygame.time.get_ticks()

                if not self._is_in_ui_panel(event.pos):
                    if event.button == 1 and pygame.key.get_mods() & pygame.KMOD_CTRL:
                        self.script.handle_ctrl_left_click(event.pos)
                    elif event.button == 1:
                        if current_time - self.last_click_time < 200:
                            self.script.handle_double_click(event.pos)
                        else:
                            self.script.handle_left_click(event.pos)
                    elif event.button == 3:
                        self.script.handle_right_click(event.pos)

                self.last_click_time = current_time

            elif event.type == pygame.MOUSEBUTTONUP:
                if not self._is_in_ui_panel(event.pos):
                    if event.button == 1:
                        self.script.handle_left_click_release(event.pos)

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.script.handle_escape_keydown()
                elif event.key == pygame.K_SPACE:
                    self.script.toggle_pause()
                elif event.key == pygame.K_RIGHT:
                    self.script.perform_single_step()
                elif event.key == pygame.K_DELETE:
                    self.script.handle_delete_keydown()
                elif event.key == pygame.K_TAB:
                    self.script.switch_mode(
                        Mode.PHYSICS 
                        if self.script.mode == Mode.OBSTACLE 
                        else Mode.OBSTACLE
                    )
                elif event.key == pygame.K_r:
                    self.script.reset_simulation()
                elif event.key == pygame.K_g:
                    self.script.toggle_gravity()

        if pygame.mouse.get_pressed()[0]:
            self.script.handle_left_click_hold(pygame.mouse.get_pos())


        return True

    def update(self, delta_time) -> None:
        self.script.update(delta_time)
        for element in self.ui_elements:
            element.update()

    def render(self) -> None:
        self.screen.fill(BG_COLOR)

        # Draw springs
        for spring in self.script.springs:
            spring.draw(self.screen)

        # Draw mass points
        for point in self.script.mass_points:
            point.draw(self.screen)

        # Draw obstacles
        for obstacle in self.script.obstacles:
            obstacle.draw(self.screen)

        # Draw in-progress obstacle
        drawing_obstacle, obstacle_points = self.script.drawing_obstacle, self.script.drawing_obstacle_points
        if drawing_obstacle and len(obstacle_points) > 0:
            tuple_points = [tuple(p) for p in obstacle_points]
            if len(tuple_points) > 1:
                pygame.draw.lines(self.screen, (255, 100, 100), False, tuple_points, 2)

            for point in tuple_points:
                pygame.draw.circle(self.screen, (255, 100, 100), point, 5)

            mouse_pos = pygame.mouse.get_pos()
            if not self._is_in_ui_panel(mouse_pos):
                pygame.draw.line(
                    self.screen, (255, 100, 100), tuple_points[-1], mouse_pos, 1
                )

        # Draw all UI elements
        for element in self.ui_elements:
            element.draw(self.screen)

        pygame.display.update()
