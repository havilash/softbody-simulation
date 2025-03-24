import pygame
from softbody_simulation.ui import Panel, Button, Text, Slider
from softbody_simulation.scripts.sandbox import Selection, Mode
from softbody_simulation.consts import FONT, FONT_COLOR, TRANSPARENT_COLOR, TRANSPARENT_HOVER_COLOR
from softbody_simulation.consts import (
    WIN_SIZE,
    FONT,
    FONT_COLOR,
    TRANSPARENT_COLOR,
    TRANSPARENT_HOVER_COLOR,
)


class SandboxPanel(Panel):
    WIDTH = 180
    PADDING = 15
    ELEMENT_GAP = 50  
    COLOR = "#0a5c9e"

    def __init__(self, script):
        panel_x = WIN_SIZE[0] - self.WIDTH - 15
        panel_y = 15
        panel_rect = pygame.Rect(panel_x, panel_y, self.WIDTH, 220)
        
        super().__init__(panel_rect, color=self.COLOR, border_radius=5, border_width=1, border_color=(255, 255, 255, 100))
        self.script = script
        self.padding = self.PADDING
        self.element_gap = self.ELEMENT_GAP

        self._last_state = {
            'mass_count': 0,
            'spring_count': 0,
            'obstacle_count': 0,
            'mode': None,
        }
        
        self.build_ui_elements()
    
    def build_ui_elements(self):
        self.clear_elements()
        elements = []

        base_x = self.rect.x + self.rect.width // 2
        base_y = self.rect.y + self.padding

        # Mode Toggle Button
        mode_button = Button(
            pos=(base_x - 70, base_y),  # Centered properly
            size=(140, 35),  # Bigger button
            text=self._get_mode_button_text(),
            font=FONT,
            font_size=18,  # Slightly larger font
            font_color=FONT_COLOR,
            color=TRANSPARENT_COLOR,
            hover_color=TRANSPARENT_HOVER_COLOR,
            callback=self._toggle_mode,
        )
        elements.append(mode_button)

        base_y += 45  # Spacing after button

        if self.script.mode == Mode.PHYSICS:
            elements.extend(self.build_physics_ui(base_x, base_y))
        else:
            elements.extend(self.build_obstacle_ui(base_x, base_y))
        
        self.add_elements(elements)
        self.update_boundary_box()

    def build_physics_ui(self, base_x, base_y):
        elements = []
        ui_configs = []

        selected_mass_points = [p for p in self.script.mass_points if p.selected]
        if selected_mass_points or self.script.selection == Selection.MASS_POINT:
            mass_value = selected_mass_points[0].mass if selected_mass_points else self.script.default_mass
            if self.script.selection == Selection.MASS_POINT:
                ui_configs.append(("Mass", (1, 200), mass_value, self.script.update_mass))

        selected_springs = [s for s in self.script.springs if s.selected]
        if selected_springs or self.script.selection == Selection.SPRING:
            spring_stiffness = selected_springs[0].stiffness if selected_springs else self.script.default_stiffness
            spring_rest_length = selected_springs[0].rest_length if selected_springs else self.script.default_rest_length
            spring_damping = selected_springs[0].damping if selected_springs else self.script.default_damping
            if self.script.selection == Selection.SPRING:
                ui_configs.extend([
                    ("Stiffness", (0, 300), spring_stiffness, self.script.update_stiffness),
                    ("Rest Length", (0, 300), spring_rest_length, self.script.update_rest_length),
                    ("Damping", (0, 100), spring_damping, self.script.update_damping),
                ])

        selection_lines = []
        if selected_mass_points:
            selection_lines.append(f"Selected masses: {len(selected_mass_points)}")
        if selected_springs:
            selection_lines.append(f"Selected springs: {len(selected_springs)}")

        if selection_lines:
            elements.append(Text(
                center_pos=(base_x, base_y),
                text="\n".join(selection_lines),
                size=16,  # Larger text for readability
            ))
            base_y += 30 * len(selection_lines)

        for idx, (label, vrange, value, callback) in enumerate(ui_configs):
            y_offset = base_y + self.element_gap * idx
            elements.append(Text(
                center_pos=(base_x, y_offset),
                text=label,
                size=16  # Consistent font size
            ))
            elements.append(Slider(
                pos=(base_x - 60, y_offset + self.element_gap / 3),
                size=(120, 8),  # Larger slider for better interaction
                vrange=vrange,
                value=value,
                callback=callback,
            ))

        if not ui_configs:
            elements.append(Text(
                center_pos=(base_x, base_y),
                text="Select objects",
                size=16,  # More readable
            ))
            elements.append(Text(
                center_pos=(base_x, base_y + self.element_gap / 3),
                text="to edit properties",
                size=16,
            ))

            controls = [
                "Controls:",
                "Left click - Select",
                "Right click - Create",
                "Ctrl + Left click - Add to selection",
                "DELETE - Remove selected",
                "Right arrow - Step",
                "Space - Pause",
                "ESC - Cancel",
            ]

            for idx, line in enumerate(controls):
                elements.append(Text(
                    center_pos=(base_x, base_y + self.element_gap + idx * 20),
                    text=line,
                    size=14,  # Consistent size
                ))

        return elements

    def build_obstacle_ui(self, base_x, base_y):
        elements = []
        selected_obstacles = [obs for obs in self.script.obstacles if obs.selected]
        obstacle_text = f"Selected: {len(selected_obstacles)}" if selected_obstacles else "No obstacles selected"
        elements.append(Text(
            center_pos=(base_x, base_y),
            text=obstacle_text,
            size=16,
        ))

        hints = [
            "Controls:",
            "Left Click - Select", # TODO: implement 
            "Right Click - Create",
            "Ctrl + Left Click - Add to selection",
            "DELETE - Remove selected",
            "Right arrow - Step",
            "Space - Pause",
            "ESC - Cancel",
        ]
        for idx, hint in enumerate(hints):
            elements.append(Text(
                center_pos=(base_x, base_y + self.element_gap / 2 + idx * 18),
                text=hint,
                size=14,
            ))

        return elements

    def _get_mode_button_text(self):
        return "Physics" if self.script.mode == Mode.PHYSICS else "Obstacle"
    
    def _toggle_mode(self):
        new_mode = Mode.PHYSICS if self.script.mode == Mode.OBSTACLE else Mode.OBSTACLE
        self.script.switch_mode(new_mode)
    
    def update(self):
        """Rebuilds the UI when any tracked state has changed."""
        super().update()
        current_state = {
            'mass_count': len([p for p in self.script.mass_points if p.selected]),
            'spring_count': len([s for s in self.script.springs if s.selected]),
            'obstacle_count': len([o for o in self.script.obstacles if o.selected]),
            'mode': self.script.mode,
        }
        if current_state != self._last_state:
            self.build_ui_elements()
            self._last_state = current_state.copy()
