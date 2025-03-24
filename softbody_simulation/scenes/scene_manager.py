from softbody_simulation.consts import FPS
from softbody_simulation.scenes.scene import Scene

import pygame

import sys

from softbody_simulation.utils import Singleton


class SceneManager(Singleton):
    initialized = False

    def __init__(
        self, screen: pygame.Surface | None = None, initial_scene: Scene | None = None
    ):
        if self.initialized:
            return

        if screen is None or initial_scene is None:
            raise ValueError("SceneManager must be initialized")

        self.initialized = True
        self.screen = screen
        self.current_scene = initial_scene

    def switch_scene(self, new_scene: Scene):
        self.current_scene = new_scene

    def run(self):
        clock = pygame.time.Clock()
        running = True
        while running:
            clock.tick(FPS)
            current_fps = clock.get_fps()
            current_fps = current_fps if current_fps > 0 else FPS
            delta_time = 1 / current_fps

            if not self.current_scene.handle_events():
                running = False
                break

            self.current_scene.update(delta_time)
            self.current_scene.render()
        pygame.quit()
        sys.exit()
