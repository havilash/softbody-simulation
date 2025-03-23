import pygame
from .element import UIElement

class Panel(UIElement):
    """
    A container UI element that can group and manage other UI elements.
    The panel provides a background and manages contained elements.
    """
    def __init__(self, rect, color="#0a5c9e", border_radius=0, border_width=0, border_color=(255, 255, 255)):
        """
        Initialize a new UI panel.
        
        Args:
            rect (pygame.Rect): The position and size of the panel
            color (str or tuple): Background color of the panel
            border_radius (int): Radius for rounded corners (0 for square corners)
            border_width (int): Width of the panel border (0 for no border)
            border_color (tuple): Color of the border
        """
        self.rect = rect
        self.color = color
        self.border_radius = border_radius
        self.border_width = border_width
        self.border_color = border_color
        self.elements = []
        self.draggable = False
        self.dragging = False
        self.drag_offset = (0, 0)
        
    def add_element(self, element):
        """Add a UI element to the panel."""
        self.elements.append(element)
        
    def add_elements(self, elements):
        """Add multiple UI elements to the panel."""
        self.elements.extend(elements)
        
    def clear_elements(self):
        """Remove all elements from the panel."""
        self.elements = []
        
    def set_draggable(self, draggable=True):
        """Enable or disable panel dragging functionality."""
        self.draggable = draggable
        
    def contains_point(self, pos):
        """Check if the panel contains the given point."""
        return self.rect.collidepoint(pos)
    
    def handle_event(self, event: pygame.event.Event):
        """Handle panel events and pass events to children."""
        # Handle dragging
        if self.draggable:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.contains_point(event.pos):
                    self.dragging = True
                    self.drag_offset = (
                        event.pos[0] - self.rect.x,
                        event.pos[1] - self.rect.y
                    )
            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                self.dragging = False
            elif event.type == pygame.MOUSEMOTION and self.dragging:
                self.rect.x = event.pos[0] - self.drag_offset[0]
                self.rect.y = event.pos[1] - self.drag_offset[1]

        # Pass events to all contained elements
        for element in self.elements:
            element.handle_event(event)

    def update(self):
        """Update all contained UI elements."""
        for element in self.elements:
            element.update()

    def draw(self, screen: pygame.Surface):
        """Draw the panel and all contained elements."""
        # Draw panel background
        if self.border_radius > 0:
            pygame.draw.rect(screen, self.color, self.rect, 0, self.border_radius)
            if self.border_width > 0:
                pygame.draw.rect(screen, self.border_color, self.rect, 
                                self.border_width, self.border_radius)
        else:
            pygame.draw.rect(screen, self.color, self.rect)
            if self.border_width > 0:
                pygame.draw.rect(screen, self.border_color, self.rect, self.border_width)

        # Draw all contained elements
        for element in self.elements:
            element.draw(screen)
