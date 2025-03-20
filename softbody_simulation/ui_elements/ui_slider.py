import pygame
from .ui_element import UIElement


class UISlider(UIElement):
    def __init__(self, pos, size, vrange=(0, 1), value=0, callback=None):
        self.vrange = vrange
        self.rect = pygame.Rect(*pos, *size)
        self.callback = callback
        self.value = value if vrange[0] <= value <= vrange[1] else vrange[0]
        self.circle_radius = int(self.rect.h * 1.5)
        self.update_circle_position()

    def update_circle_position(self):
        ratio = (self.value - self.vrange[0]) / (self.vrange[1] - self.vrange[0])
        self.circle_x = self.rect.x + ratio * self.rect.w
        self.circle_y = self.rect.y + self.rect.h // 2

    def handle_event(self, event: pygame.event.Event):
        if event.type in (pygame.MOUSEBUTTONDOWN, pygame.MOUSEMOTION):
            if event.type == pygame.MOUSEBUTTONDOWN and event.button != 1:
                return
            if pygame.mouse.get_pressed()[0]:
                if self.is_over(event.pos):
                    self.set_position(event.pos[0])
                    if self.callback:
                        self.callback(self.value)

    def is_over(self, pos):
        in_rect = self.rect.collidepoint(pos)
        dist = abs(pos[0] - self.circle_x)
        in_circle = (
            dist <= self.circle_radius
            and abs(pos[1] - self.circle_y) <= self.circle_radius
        )
        return in_rect or in_circle

    def set_position(self, x):
        if x < self.rect.x:
            self.circle_x = self.rect.x
        elif x > self.rect.x + self.rect.w:
            self.circle_x = self.rect.x + self.rect.w
        else:
            self.circle_x = x

        self.value = ((self.circle_x - self.rect.x) / float(self.rect.w)) * (
            self.vrange[1] - self.vrange[0]
        ) + self.vrange[0]

    def update(self):
        # No periodic update needed.
        pass

    def draw(self, screen: pygame.Surface):
        pygame.draw.rect(screen, (255, 255, 255), self.rect)
        pygame.draw.circle(
            screen,
            (255, 240, 255),
            (int(self.circle_x), int(self.circle_y)),
            self.circle_radius,
        )
