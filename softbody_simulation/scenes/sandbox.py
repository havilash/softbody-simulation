import pygame
from softbody_simulation.consts import (
    BG_COLOR,
    WIN_SIZE,
    FONT,
    FONT_COLOR,
    TRANSPARENT_COLOR,
    TRANSPARENT_HOVER_COLOR,
)
from softbody_simulation.scenes.scene import UIScene
from softbody_simulation.scenes.scene_manager import SceneManager
from softbody_simulation.scripts.sandbox import SandboxScript
from softbody_simulation.ui_elements.ui_button import UIButton
from softbody_simulation.ui_elements.ui_slider import UISlider
from softbody_simulation.ui_elements.ui_text import UIText


def create_slider_with_label(label_text, pos, vrange, value, callback):
    """Create a slider with a descriptive label."""
    label = UIText(center_pos=(pos[0], pos[1]), text=label_text, size=20)
    slider = UISlider(
        pos=(pos[0] - 50, pos[1] + 20),
        size=(100, 5),
        vrange=vrange,
        value=value,
        callback=callback,
    )
    return label, slider


class SandboxScene(UIScene):
    # Constants for UI layout
    UI_PANEL_WIDTH = 150
    UI_PANEL_PADDING = 20
    UI_ELEMENT_GAP = 50

    def __init__(self, screen: pygame.Surface):
        super().__init__(screen, background_color=BG_COLOR)
        self.script = SandboxScript(
            default_mass=100,
            default_stiffness=100,
            default_rest_length=50,
            default_damping=10,
        )

        # Initialize state variables
        self.current_mode = "physics"
        self.current_ui_group = "all"

        # Removed multi-select state variable

        # Create UI elements
        self.back_button = UIButton(
            pos=(10, 10),
            size=(100, 40),
            text="Back",
            font=FONT,
            font_size=20,
            font_color=FONT_COLOR,
            color=TRANSPARENT_COLOR,
            hover_color=TRANSPARENT_HOVER_COLOR,
            callback=self.go_back,
        )

        self.static_ui_elements = [self.back_button]
        self.dynamic_elements = self.build_dynamic_elements()
        self.ui_elements = self.static_ui_elements + self.dynamic_elements

    def go_back(self):
        """Navigate back to the main menu scene."""
        from scenes.main_menu import MainMenuScene

        SceneManager().switch_scene(MainMenuScene(self.screen))

    def toggle_mode(self):
        """Toggle between physics and obstacle modes."""
        if self.current_mode == "physics":
            self.current_mode = "obstacle"
            self.script.clear_physics_selections()
        else:
            self.current_mode = "physics"

        self.script.cancel_obstacle_drawing()

        self.dynamic_elements = self.build_dynamic_elements()
        self.ui_elements = self.static_ui_elements + self.dynamic_elements

    def build_dynamic_elements(self):
        """Build dynamic UI elements based on current state."""
        elements = []

        # Calculate panel dimensions
        panel_x = WIN_SIZE[0] - self.UI_PANEL_WIDTH - 10
        panel_y = 10

        # Center position for UI elements
        base_x = panel_x + self.UI_PANEL_WIDTH / 2
        base_y = panel_y + self.UI_PANEL_PADDING

        # Add mode toggle button
        mode_button_text = "Physics" if self.current_mode == "physics" else "Obstacle"
        mode_button = UIButton(
            pos=(base_x - 60, base_y),
            size=(120, 30),
            text=mode_button_text,
            font=FONT,
            font_size=16,
            font_color=FONT_COLOR,
            color=TRANSPARENT_COLOR,
            hover_color=TRANSPARENT_HOVER_COLOR,
            callback=self.toggle_mode,
        )
        elements.append(mode_button)

        # Removed multi-select toggle button

        # Increment base_y for next elements (using less space now)
        base_y += 40

        # Prepare UI configs based on current mode and selection
        ui_configs = []
        if self.current_mode == "physics":
            # Prepare mass configs
            has_selected_mass_points = len(self.script.selected_mass_points) > 0
            mass_value = (
                self.script.selected_mass_points[0].mass
                if has_selected_mass_points
                else self.script.default_mass
            )
            mass_configs = [
                (
                    (
                        f"Mass ({len(self.script.selected_mass_points)} selected)"
                        if has_selected_mass_points
                        else "Mass"
                    ),
                    (1, 200),
                    mass_value,
                    self.script.update_mass,
                ),
            ]

            # Prepare spring configs
            has_selected_springs = len(self.script.selected_springs) > 0
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
                    (
                        f"Stiffness ({len(self.script.selected_springs)} selected)"
                        if has_selected_springs
                        else "Stiffness"
                    ),
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

            # Select which configs to show based on current UI group
            if self.current_ui_group == "all":
                ui_configs = mass_configs + spring_configs
            elif self.current_ui_group == "mass":
                ui_configs = mass_configs
            elif self.current_ui_group == "spring":
                ui_configs = spring_configs

            # Create sliders with labels for each configuration
            for i, (label, vrange, value, callback) in enumerate(ui_configs):
                label_ui, slider_ui = create_slider_with_label(
                    label,
                    (base_x, base_y + self.UI_ELEMENT_GAP * i),
                    vrange,
                    value,
                    callback,
                )
                elements.extend([label_ui, slider_ui])

            # Create "Clear Selection" button
            if (
                has_selected_mass_points
                or has_selected_springs
                or len(self.script.selected_obstacles) > 0
            ):
                clear_y = base_y + self.UI_ELEMENT_GAP * len(ui_configs) + 20
                clear_button = UIButton(
                    pos=(base_x - 60, clear_y),
                    size=(120, 30),
                    text="Clear Selection",
                    font=FONT,
                    font_size=16,
                    font_color=FONT_COLOR,
                    color=TRANSPARENT_COLOR,
                    hover_color=TRANSPARENT_HOVER_COLOR,
                    callback=self.script.clear_all_selections,
                )
                elements.append(clear_button)
        else:
            obstacle_text = (
                f"Selected: {len(self.script.selected_obstacles)}"
                if len(self.script.selected_obstacles) > 0
                else "No obstacles selected"
            )
            elements.append(
                UIText(
                    center_pos=(base_x, base_y),
                    text=obstacle_text,
                    size=16,
                )
            )

            hint_texts = [
                UIText(
                    center_pos=(base_x, base_y + 30),
                    text="Left click to add points",
                    size=14,
                ),
                UIText(
                    center_pos=(base_x, base_y + 50),
                    text="Right click to complete",
                    size=14,
                ),
                UIText(
                    center_pos=(base_x, base_y + 70),
                    text="ESC to cancel",
                    size=14,
                ),
            ]
            elements.extend(hint_texts)

        ui_config_count = len(ui_configs) if self.current_mode == "physics" else 0
        panel_height = 70 + (7 + self.UI_ELEMENT_GAP) * max(
            ui_config_count, 1
        )  # Reduced height since we removed multi-select
        if self.current_mode == "physics" and (
            len(self.script.selected_mass_points) > 0
            or len(self.script.selected_springs) > 0
        ):
            panel_height += 50
        if self.current_mode == "obstacle":
            panel_height += 60

        self.ui_panel = pygame.Rect(panel_x, panel_y, self.UI_PANEL_WIDTH, panel_height)

        return elements

    # Removed toggle_multi_select method

    def _is_in_ui_panel(self, pos):
        return self.ui_panel.collidepoint(pos)

    def handle_events(self) -> bool:
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                return False

            # Dispatch events to UI elements
            for element in self.ui_elements:
                element.handle_event(event)

            if event.type == pygame.MOUSEBUTTONDOWN:
                if not self._is_in_ui_panel(event.pos):
                    if self.current_mode == "physics":
                        elif event.button == 1 and pygame.key.get_mods() & pygame.KMOD_CTRL:
                            self.script.handle_ctrl_left_click(event.pos)
                        if event.button == 1:
                            self.script.handle_left_click(event.pos)
                        elif event.button == 3:
                            self.script.handle_right_click(event.pos)
                    else:
                        if event.button == 1:
                            if self.script.drawing_obstacle:
                                self.script.handle_obstacle_click(event.pos)
                            else:
                                obstacle = self.script.get_obstacle_at(event.pos)
                                if obstacle:
                                    self.script.select_obstacle(obstacle)
                                else:
                                    self.script.handle_obstacle_click(event.pos)
                        elif event.button == 3 and self.script.drawing_obstacle:
                            self.script.complete_obstacle()

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.script.handle_escape_keydown(event.key)
                elif event.key == pygame.K_SPACE:
                    self.script.toggle_pause(event.key)
                elif event.key == pygame.K_RIGHT:
                    self.script.perform_single_step(event.key)
                elif event.key == pygame.K_DELETE:
                    if self.current_mode == "physics":
                        self.script.handle_delete()
                    else:
                        self.script.delete_selected_obstacles()
                elif event.key == pygame.K_TAB:
                    self.toggle_mode()

        return True

    def update(self, delta_time) -> None:
        self.script.update(delta_time)

        for element in self.ui_elements:
            element.update()

        if self.current_mode == "physics":
            desired_group = "all"
            if len(self.script.selected_springs) > 0:
                desired_group = "spring"
            elif len(self.script.selected_mass_points) > 0:
                desired_group = "mass"

            if desired_group != self.current_ui_group:
                self.current_ui_group = desired_group
                self.dynamic_elements = self.build_dynamic_elements()
                self.ui_elements = self.static_ui_elements + self.dynamic_elements

        # Rebuild UI elements if number of selected objects changed
        last_mass_count = getattr(self, "_last_mass_count", 0)
        last_spring_count = getattr(self, "_last_spring_count", 0)
        last_obstacle_count = getattr(self, "_last_obstacle_count", 0)

        current_mass_count = len(self.script.selected_mass_points)
        current_spring_count = len(self.script.selected_springs)
        current_obstacle_count = len(self.script.selected_obstacles)

        if (
            last_mass_count != current_mass_count
            or last_spring_count != current_spring_count
            or last_obstacle_count != current_obstacle_count
        ):
            self.dynamic_elements = self.build_dynamic_elements()
            self.ui_elements = self.static_ui_elements + self.dynamic_elements

            self._last_mass_count = current_mass_count
            self._last_spring_count = current_spring_count
            self._last_obstacle_count = current_obstacle_count

    def render(self) -> None:
        """Render the scene to the screen."""
        self.screen.fill(BG_COLOR)

        # Draw springs
        for spring in self.script.springs:
            spring.draw(self.screen)
            if spring in self.script.selected_springs:
                p1, p2 = spring.a.pos, spring.b.pos
                pygame.draw.line(self.screen, (255, 255, 0), p1, p2, 4)

        # Draw mass points
        for point in self.script.mass_points:
            point.draw(self.screen)
            # Removed yellow highlight circle for selected mass points

        # Draw obstacles
        for obstacle in self.script.obstacles:
            obstacle.draw(self.screen)
            if obstacle in self.script.selected_obstacles:
                # Highlight selected obstacle
                points = obstacle.points
                if len(points) > 0:
                    tuple_points = [tuple(v) for v in points]
                    pygame.draw.lines(self.screen, (255, 255, 0), True, tuple_points, 3)
                    # Draw a dot at each vertex
                    for point in tuple_points:
                        pygame.draw.circle(self.screen, (255, 255, 0), point, 5)

        drawing_obstacle, obstacle_points = self.script.get_obstacle_drawing_state()
        if drawing_obstacle and len(obstacle_points) > 0:
            tuple_points = [tuple(p) for p in obstacle_points]
            if len(tuple_points) > 1:
                pygame.draw.lines(self.screen, (255, 100, 100), False, tuple_points, 2)

            for point in tuple_points:
                pygame.draw.circle(self.screen, (255, 100, 100), point, 5)

            mouse_pos = pygame.mouse.get_pos()
            if not self._is_in_ui_panel(mouse_pos):
                pygame.draw.line(
                    self.screen, (255, 100, 100), tuple_points[-1], mouse_pos, 1
                )

        pygame.draw.rect(self.screen, "#0a5c9e", self.ui_panel)

        # Draw all UI elements
        for element in self.ui_elements:
            element.draw(self.screen)

        pygame.display.update()
