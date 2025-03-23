import pygame
from .element import UIElement


class Button(UIElement):
    def __init__(
        self,
        pos,
        size,
        text=None,
        font="helvetica",
        font_size=None,
        font_color="white",
        color="black",
        hover_color="black",
        callback=None,
    ):
        # Create the button rectangle and store colors.
        self.rect = pygame.Rect(*pos, *size)
        self.base_color = color
        self.hover_color = hover_color
        self.current_color = self.base_color
        self.callback = callback

        # Setup font and text.
        self.font_size = font_size if font_size is not None else int(size[1] * 0.7)
        if font.endswith((".ttf", ".otf")):
            self.font = pygame.font.Font(font, self.font_size)
        else:
            self.font = pygame.font.SysFont(font, self.font_size)
        self.font_color = font_color
        self.text = text
        self.text_surface = None
        if self.text:
            self.text_surface = self.font.render(self.text, True, self.font_color)

    def handle_event(self, event: pygame.event.Event):
        if event.type == pygame.MOUSEMOTION:
            if self.rect.collidepoint(event.pos):
                self.current_color = self.hover_color
            else:
                self.current_color = self.base_color
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1 and self.rect.collidepoint(event.pos):
                if self.callback:
                    self.callback()

    def update(self):
        # No dynamic state for this button.
        pass

    def draw(self, screen: pygame.Surface):
        pygame.draw.rect(screen, self.current_color, self.rect)
        if self.text_surface:
            text_rect = self.text_surface.get_rect(center=self.rect.center)
            screen.blit(self.text_surface, text_rect)
