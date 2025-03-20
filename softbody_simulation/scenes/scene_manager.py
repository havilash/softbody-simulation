from softbody_simulation.consts import FPS
from softbody_simulation.scenes.scene import Scene, set_scene_manager

import pygame

import sys


class SceneManager:
    def __init__(self, screen: pygame.Surface, initial_scene: Scene):
        self.screen = screen
        self.current_scene = initial_scene
        set_scene_manager(self)  # Set global reference

    def switch_scene(self, new_scene: Scene):
        self.current_scene = new_scene

    def run(self):
        clock = pygame.time.Clock()
        running = True
        while running:
            clock.tick(FPS)
            current_fps = clock.get_fps()
            delta_time = current_fps if current_fps > 0 else FPS

            if not self.current_scene.handle_events():
                running = False
                break

            self.current_scene.update(delta_time)
            self.current_scene.render()
        pygame.quit()
        sys.exit()