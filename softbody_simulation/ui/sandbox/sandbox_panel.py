from softbody_simulation.ui import Panel, Button, Text, Slider
from softbody_simulation.scripts.sandbox import Mode
from softbody_simulation.consts import FONT, FONT_COLOR, TRANSPARENT_COLOR, TRANSPARENT_HOVER_COLOR


class SandboxPanel(Panel):
    """
    A specialized UI panel for the sandbox view that manages physics and obstacle mode controls.
    This panel dynamically adjusts its contents based on the current mode and selection state.
    """
    
    def __init__(self, rect, script, padding=20, element_gap=50, color="#0a5c9e"):
        """
        Initialize a SandboxUIPanel.
        
        Args:
            rect (pygame.Rect): The position and size of the panel
            script (SandboxScript): Reference to the sandbox script for callbacks
            padding (int): Internal padding of elements from panel edges
            element_gap (int): Vertical spacing between UI elements
            color (str): Background color of the panel
        """
        super().__init__(rect, color=color, border_radius=5, border_width=1, border_color=(255, 255, 255, 100))
        self.script = script
        self.padding = padding
        self.element_gap = element_gap
        
        # Store state information to detect changes
        self._last_mass_count = 0
        self._last_spring_count = 0
        self._last_obstacle_count = 0
        self._last_mode = None
        
        # Build initial UI
        self.build_ui_elements()
    
    def build_ui_elements(self):
        """Build all UI elements based on current state"""
        self.clear_elements()
        elements = []
        
        # Calculate base positions
        base_x = self.rect.x + self.rect.width / 2
        base_y = self.rect.y + self.padding
        
        # Mode toggle button
        mode_button_text = self.script.get_current_mode_display_text()
        mode_button = Button(
            pos=(base_x - 60, base_y),
            size=(120, 30),
            text=mode_button_text,
            font=FONT,
            font_size=16,
            font_color=FONT_COLOR,
            color=TRANSPARENT_COLOR,
            hover_color=TRANSPARENT_HOVER_COLOR,
            callback=self.script.toggle_mode,
        )
        elements.append(mode_button)
        
        base_y += 40
        
        if self.script.is_physics_mode():
            physics_elements = self.build_physics_ui(base_x, base_y)
            elements.extend(physics_elements)
        else:
            obstacle_elements = self.build_obstacle_ui(base_x, base_y)
            elements.extend(obstacle_elements)
        
        # Add all elements to the panel
        self.add_elements(elements)
        
        # Adjust panel height based on content
        self.update_panel_height()
    
    def build_physics_ui(self, base_x, base_y):
        """Build UI elements for physics mode"""
        elements = []
        ui_configs = []
        
        # Handle mass point controls
        has_selected_mass_points = len(self.script.selected_mass_points) > 0
        if has_selected_mass_points or self.script.current_mode in [Mode.PHYSICS_ALL, Mode.PHYSICS_MASS]:
            mass_value = (
                self.script.selected_mass_points[0].mass
                if has_selected_mass_points
                else self.script.default_mass
            )
            mass_configs = [
                (
                    "Mass",
                    (1, 200),
                    mass_value,
                    self.script.update_mass,
                ),
            ]
            
            if self.script.current_mode in [Mode.PHYSICS_ALL, Mode.PHYSICS_MASS]:
                ui_configs.extend(mass_configs)
        
        # Handle spring controls
        has_selected_springs = len(self.script.selected_springs) > 0
        if has_selected_springs or self.script.current_mode in [Mode.PHYSICS_ALL, Mode.PHYSICS_SPRING]:
            spring_stiffness = (
                self.script.selected_springs[0].stiffness
                if has_selected_springs
                else self.script.default_stiffness
            )
            spring_rest_length = (
                self.script.selected_springs[0].rest_length
                if has_selected_springs
                else self.script.default_rest_length
            )
            spring_damping = (
                self.script.selected_springs[0].damping
                if has_selected_springs
                else self.script.default_damping
            )
            
            spring_configs = [
                (
                    "Stiffness",
                    (0, 300),
                    spring_stiffness,
                    self.script.update_stiffness,
                ),
                (
                    "Rest Length",
                    (0, 300),
                    spring_rest_length,
                    self.script.update_rest_length,
                ),
                (
                    "Damping",
                    (0, 100),
                    spring_damping,
                    self.script.update_damping,
                ),
            ]
            
            if self.script.current_mode in [Mode.PHYSICS_ALL, Mode.PHYSICS_SPRING]:
                ui_configs.extend(spring_configs)
        
        # Add selection info
        selection_text = []
        if has_selected_mass_points:
            selection_text.append(f"Selected masses: {len(self.script.selected_mass_points)}")
        if has_selected_springs:
            selection_text.append(f"Selected springs: {len(self.script.selected_springs)}")
        
        if selection_text:
            selection_info = Text(
                center_pos=(base_x, base_y),
                text="\n".join(selection_text),
                size=14
            )
            elements.append(selection_info)
            base_y += 30 * len(selection_text)
        
        # Create sliders for all configurations
        for i, (label, vrange, value, callback) in enumerate(ui_configs):
            label_ui = Text(
                center_pos=(base_x, base_y + self.element_gap * i),
                text=label,
                size=20
            )
            slider_ui = Slider(
                pos=(base_x - 50, base_y + self.element_gap * i + 20),
                size=(100, 5),
                vrange=vrange,
                value=value,
                callback=callback,
            )
            elements.extend([label_ui, slider_ui])
        
        # Add control hints
        if not ui_configs:
            hint = Text(
                center_pos=(base_x, base_y),
                text="Select objects to edit properties",
                size=14
            )
            elements.append(hint)
            
            controls_hint = [
                "Controls:",
                "Click - Select/Create",
                "Ctrl+Click - Add to selection",
                "Delete - Remove selected",
                "Space - Toggle simulation",
                "Right arrow - Step simulation",
            ]
            
            for i, text in enumerate(controls_hint):
                elements.append(Text(
                    center_pos=(base_x, base_y + 30 + i * 20),
                    text=text,
                    size=12
                ))
        
        return elements
    
    def build_obstacle_ui(self, base_x, base_y):
        """Build UI elements for obstacle mode"""
        elements = []
        
        # Show selection info
        obstacle_text = (
            f"Selected: {len(self.script.selected_obstacles)}"
            if len(self.script.selected_obstacles) > 0
            else "No obstacles selected"
        )
        elements.append(
            Text(
                center_pos=(base_x, base_y),
                text=obstacle_text,
                size=16,
            )
        )
        
        # Add drawing instructions
        hint_texts = [
            "Left click to add points",
            "Right click to complete",
            "ESC to cancel",
            "DELETE to remove selected"
        ]
        
        for i, text in enumerate(hint_texts):
            elements.append(
                Text(
                    center_pos=(base_x, base_y + 30 + i * 20),
                    text=text,
                    size=14,
                )
            )
        
        return elements
    
    def update_panel_height(self):
        """Update the panel height based on its content"""
        if self.script.is_physics_mode():
            # Calculate physics mode height
            control_count = 0
            
            # Count selected items which add height
            if len(self.script.selected_mass_points) > 0:
                control_count += 1  # Mass control
            
            if len(self.script.selected_springs) > 0:
                control_count += 3  # Spring controls (stiffness, rest length, damping)
            
            # Set minimum height for physics mode
            min_height = 200
            
            # Add height for controls
            height = max(
                min_height,
                70 + (self.element_gap * control_count) + (30 if control_count > 0 else 0)
            )
            
            # If no controls are showing, add space for hints
            if control_count == 0:
                height = max(height, 230)  # Space for control hints
                
        else:
            # Obstacle mode height is fixed
            height = 180
        
        # Update the rect height
        self.rect.height = height
    
    def update(self):
        """Update the panel and check for state changes"""
        super().update()
        
        # Check if we need to rebuild UI due to state changes
        current_mass_count = len(self.script.selected_mass_points)
        current_spring_count = len(self.script.selected_springs)
        current_obstacle_count = len(self.script.selected_obstacles)
        current_mode = self.script.current_mode
        
        if (
            self._last_mass_count != current_mass_count
            or self._last_spring_count != current_spring_count
            or self._last_obstacle_count != current_obstacle_count
            or self._last_mode != current_mode
        ):
            self.build_ui_elements()
            
            # Update state tracking
            self._last_mass_count = current_mass_count
            self._last_spring_count = current_spring_count
            self._last_obstacle_count = current_obstacle_count
            self._last_mode = current_mode
