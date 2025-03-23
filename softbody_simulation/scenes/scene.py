from enum import Enum
import pygame
from abc import ABC, abstractmethod
from softbody_simulation.consts import BG_COLOR
from softbody_simulation.ui_elements.ui_element import UIElement


class Scene(ABC):
    def __init__(self, screen: pygame.Surface):
        self.screen = screen

    @abstractmethod
    def handle_events(self) -> bool:
        """Process input events. Return False to exit the app."""
        pass

    @abstractmethod
    def update(self, delta_time: float) -> None:
        """Update scene state."""
        pass

    @abstractmethod
    def render(self) -> None:
        """Render scene contents."""
        pass


class UIScene(Scene):

    def __init__(self, screen: pygame.Surface, background_color=BG_COLOR):
        super().__init__(screen)
        self.background_color = background_color
        self.ui_elements = []

    def add_ui_element(self, *elements: list[UIElement]):
        self.ui_elements.extend(elements)

    def handle_events(self) -> bool:
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                return False

            for element in self.ui_elements:
                element.handle_event(event)
        return True

    def update(self, delta_time: float) -> None:
        for element in self.ui_elements:
            element.update()

    def render(self) -> None:
        self.screen.fill(self.background_color)
        for element in self.ui_elements:
            element.draw(self.screen)
        pygame.display.update()
