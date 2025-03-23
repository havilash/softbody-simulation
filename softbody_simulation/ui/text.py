import pygame
from .element import UIElement


class Text(UIElement):
    def __init__(self, center_pos, text, size=10, font="helvetica", color="black"):
        self.center_pos = center_pos
        self.text = text
        self.size = size
        self.color = color
        if font.endswith((".ttf", ".otf")):
            self.font = pygame.font.Font(font, self.size)
        else:
            self.font = pygame.font.SysFont(font, self.size)
        self.update_text_surface()

    def update_text_surface(self):
        self.text_surface = self.font.render(self.text, True, self.color)
        self.text_rect = self.text_surface.get_rect(center=self.center_pos)

    def handle_event(self, event: pygame.event.Event):
        # Static text does not handle events.
        pass

    def update(self):
        # Update method in case dynamic text is needed.
        pass

    def draw(self, screen: pygame.Surface):
        screen.blit(self.text_surface, self.text_rect)

    def set_text(self, new_text):
        self.text = new_text
        self.update_text_surface()
