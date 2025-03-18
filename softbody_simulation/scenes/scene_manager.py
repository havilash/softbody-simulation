import sys
import pygame
from abc import ABC, abstractmethod
from consts import FPS

# Global variable for scene manager (singleton‐like access)
_scene_manager = None

def get_scene_manager():
    return _scene_manager

def set_scene_manager(manager):
    global _scene_manager
    _scene_manager = manager

class Scene(ABC):
    def __init__(self, screen: pygame.Surface):
        self.screen = screen

    @abstractmethod
    def handle_events(self) -> bool:
        """Process input events. Return False to exit the app."""
        pass

    @abstractmethod
    def update(self) -> None:
        """Update scene state."""
        pass

    @abstractmethod
    def render(self) -> None:
        """Render scene contents."""
        pass

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
            if not self.current_scene.handle_events():
                running = False
                break
            self.current_scene.update()
            self.current_scene.render()
        pygame.quit()
        sys.exit()
