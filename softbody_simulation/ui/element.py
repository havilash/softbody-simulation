from abc import ABC, abstractmethod
import pygame


class UIElement(ABC):
    @abstractmethod
    def handle_event(self, event: pygame.event.Event):
        """Handle an incoming event."""
        pass

    @abstractmethod
    def update(self):
        """Update any internal state."""
        pass

    @abstractmethod
    def draw(self, screen: pygame.Surface):
        """Render the UI element."""
        pass
