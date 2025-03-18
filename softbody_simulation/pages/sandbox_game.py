import pygame
import numpy as np
from typing import Tuple, Optional, List, Callable

from softbody_simulation.consts import WIN_SIZE, BG_COLOR, FPS, FONT, FONT_COLOR
from softbody_simulation.entities import MassPoint, Spring
import pygame_ui as ui

class SandboxGame:
    """
    SandboxGame encapsulates a physics simulation with mass points and springs.
    The screen is divided between a simulation area and a UI panel for control sliders and buttons.
    """

    def __init__(self, screen: pygame.Surface) -> None:
        self.screen = screen
        self.mass_points: List[MassPoint] = []
        self.springs: List[Spring] = []
        self.selected_mass_point: Optional[MassPoint] = None
        self.selected_spring: Optional[Spring] = None

        # Simulation control flags.
        self.paused = False
        self.single_step = False

        # Default simulation parameters.
        self.default_mass = 100
        self.default_stiffness = 100
        self.default_rest_length = 50
        self.default_damping = 10

        # UI panel dimensions.
        self.ui_panel = pygame.Rect(WIN_SIZE[0] - 160, 10, 150, 300)

        # Containers for UI elements.
        self.sliders: List[ui.Slider] = []
        self.labels: List[ui.Text] = []
        self.buttons: List[ui.Button] = []

        self._initialize_ui()

    def _initialize_ui(self) -> None:
        """Initialize UI components (sliders and buttons) for simulation controls."""
        # Create sliders with dedicated update callbacks.
        mass_slider, mass_label = self._create_slider_with_label(
            text="Mass",
            slider_pos=(WIN_SIZE[0] - 135, 40),
            label_pos=(WIN_SIZE[0] - 85, 25),
            value_range=(1, 200),
            initial_value=self.default_mass,
            callback=self._update_mass,
        )
        stiffness_slider, stiffness_label = self._create_slider_with_label(
            text="Stiffness",
            slider_pos=(WIN_SIZE[0] - 135, 80),
            label_pos=(WIN_SIZE[0] - 85, 65),
            value_range=(0, 300),
            initial_value=self.default_stiffness,
            callback=self._update_stiffness,
        )
        rest_length_slider, rest_length_label = self._create_slider_with_label(
            text="Rest Length",
            slider_pos=(WIN_SIZE[0] - 135, 120),
            label_pos=(WIN_SIZE[0] - 85, 105),
            value_range=(0, 300),
            initial_value=self.default_rest_length,
            callback=self._update_rest_length,
        )
        damping_slider, damping_label = self._create_slider_with_label(
            text="Damping",
            slider_pos=(WIN_SIZE[0] - 135, 160),
            label_pos=(WIN_SIZE[0] - 85, 145),
            value_range=(0, 100),
            initial_value=self.default_damping,
            callback=self._update_damping,
        )

        self.sliders.extend(
            [mass_slider, stiffness_slider, rest_length_slider, damping_slider]
        )
        self.labels.extend(
            [mass_label, stiffness_label, rest_length_label, damping_label]
        )

        # Create control buttons.
        pause_button = self._create_button(
            pos=(WIN_SIZE[0] - 140, 220),
            size=(120, 30),
            text="Pause",
            callback=self._toggle_pause,
        )
        step_button = self._create_button(
            pos=(WIN_SIZE[0] - 140, 260),
            size=(120, 30),
            text="Step",
            callback=self._perform_single_step,
        )
        self.buttons.extend([pause_button, step_button])

        # Combine all UI elements for rendering.
        self.ui_elements = self.sliders + self.labels + self.buttons

    def _create_slider_with_label(
        self,
        text: str,
        slider_pos: Tuple[int, int],
        label_pos: Tuple[int, int],
        value_range: Tuple[float, float],
        initial_value: float,
        callback: Callable[[float], None],
    ) -> Tuple[ui.Slider, ui.Text]:
        """
        Create a slider and its label with a dedicated callback.

        Args:
            text: Label text.
            slider_pos: Position of the slider.
            label_pos: Position of the label.
            value_range: Allowed range for the slider.
            initial_value: Initial slider value.
            callback: Function to call when slider value changes.

        Returns:
            A tuple (slider, label).
        """
        slider = ui.Slider(
            slider_pos, (100, 5), vrange=value_range, value=initial_value
        )
        slider.callback = callback
        label = ui.Text(label_pos, text, size=20)
        return slider, label

    def _create_button(
        self,
        pos: Tuple[int, int],
        size: Tuple[int, int],
        text: str,
        callback: Callable,
        text_color: str = FONT_COLOR,
        normal_color: str = "#0a5c9e",
        hover_color: str = "#0d7eff",
    ) -> ui.Button:
        """
        Create a button with the provided specifications.

        Args:
            pos: Button position.
            size: Button dimensions.
            text: Button text.
            callback: Function to call when clicked.
            text_color: Color for the button text.
            normal_color: Normal background color.
            hover_color: Background color when hovered.

        Returns:
            An instance of ui.Button.
        """
        return ui.Button(
            pos,
            size,
            text=text,
            font=FONT,
            font_color=text_color,
            color=normal_color,
            hover_color=hover_color,
            func=callback,
        )

    def _toggle_pause(self, *_args) -> None:
        """Toggle the simulation pause state and update the button label accordingly."""
        self.paused = not self.paused
        for button in self.buttons:
            if button.text in ("Pause", "Resume"):
                button.text = "Resume" if self.paused else "Pause"
                break

    def _perform_single_step(self, *_args) -> None:
        """Trigger a single simulation update step if paused."""
        if self.paused:
            self.single_step = True

    def _is_in_ui_panel(self, pos: Tuple[int, int]) -> bool:
        """Check if a given position is within the UI panel area."""
        return pos[0] > WIN_SIZE[0] - self.ui_panel.width

    def process_events(self) -> bool:
        """
        Process incoming events, delegating to either the UI or simulation handlers.

        Returns:
            False if a quit event is detected.
        """
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False

            mouse_pos = pygame.mouse.get_pos()

            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.selected_mass_point = None
                self.selected_spring = None

            if event.type == pygame.MOUSEBUTTONDOWN:
                if self._is_in_ui_panel(mouse_pos):
                    self._handle_ui_interaction(event, mouse_pos)
                else:
                    self._handle_simulation_interaction(event, mouse_pos)

        return True

    def _handle_ui_interaction(
        self, event: pygame.event.Event, mouse_pos: Tuple[int, int]
    ) -> None:
        """Handle mouse events within the UI panel."""
        if event.button == 1:
            # Process button clicks.
            for button in self.buttons:
                if button.is_over(mouse_pos):
                    button.call_back(self.screen)
                    return
            # Process slider adjustments.
            for slider in self.sliders:
                if slider.is_over(mouse_pos):
                    slider.update(mouse_pos[0])
                    slider.call_back()
                    break

    def _handle_simulation_interaction(
        self, event: pygame.event.Event, mouse_pos: Tuple[int, int]
    ) -> None:
        """
        Handle events in the simulation area.
        Left-click selects objects or connects them with springs; right-click adds a mass point.
        """
        if event.button == 1:
            mass_point = self._get_mass_point_at(mouse_pos)
            if mass_point:
                if self.selected_mass_point and self.selected_mass_point != mass_point:
                    new_spring = Spring(
                        (self.selected_mass_point, mass_point),
                        stiffness=self.default_stiffness,
                        rest_length=self.default_rest_length,
                        damping=self.default_damping,
                    )
                    self.springs.append(new_spring)
                    self.selected_mass_point = None
                else:
                    self.selected_mass_point = mass_point
                    self.selected_spring = None
            else:
                spring = self._get_spring_at(mouse_pos)
                if spring:
                    self.selected_spring = spring
                    self.selected_mass_point = None
                else:
                    self.selected_mass_point = None
                    self.selected_spring = None
        elif event.button == 3:
            new_point = MassPoint(np.array(mouse_pos), self.default_mass)
            self.mass_points.append(new_point)

    def _get_mass_point_at(
        self, pos: Tuple[int, int], radius: int = 10
    ) -> Optional[MassPoint]:
        """
        Retrieve the first mass point within 'radius' of the given position.
        """
        for point in self.mass_points:
            if np.linalg.norm(point.pos - np.array(pos)) <= radius:
                return point
        return None

    def _get_spring_at(
        self, pos: Tuple[int, int], threshold: int = 5
    ) -> Optional[Spring]:
        """
        Retrieve the first spring whose line is within 'threshold' distance of the given position.
        """
        for spring in self.springs:
            p1, p2 = spring.mass_points[0].pos, spring.mass_points[1].pos
            if self._distance_point_to_line(np.array(pos), p1, p2) <= threshold:
                return spring
        return None

    @staticmethod
    def _distance_point_to_line(
        point: np.ndarray, start: np.ndarray, end: np.ndarray
    ) -> float:
        """
        Calculate the shortest distance from a point to a line segment defined by start and end.
        """
        if np.array_equal(start, end):
            return np.linalg.norm(point - start)
        t = np.dot(point - start, end - start) / np.dot(end - start, end - start)
        t = max(0, min(1, t))
        projection = start + t * (end - start)
        return np.linalg.norm(point - projection)

    def update_simulation(self) -> None:
        """Update all simulation objects (mass points and springs)."""
        for point in self.mass_points:
            point.update()
        for spring in self.springs:
            spring.update()

    def update(self) -> None:
        """
        Update the simulation.
        If paused, only update if a single step was triggered.
        """
        if self.paused:
            if self.single_step:
                self.update_simulation()
                self.single_step = False
        else:
            self.update_simulation()

    def render(self) -> None:
        """Render the simulation and UI components."""
        self.screen.fill(BG_COLOR)
        pygame.draw.rect(self.screen, "#0a5c9e", self.ui_panel)

        for element in self.ui_elements:
            element.draw(self.screen)

        # Draw springs, highlighting the selected spring.
        for spring in self.springs:
            spring.draw(self.screen)
            if spring == self.selected_spring:
                p1, p2 = spring.mass_points[0].pos, spring.mass_points[1].pos
                pygame.draw.line(self.screen, (255, 255, 0), p1, p2, 4)

        # Draw mass points, highlighting the selected mass point.
        for point in self.mass_points:
            point.draw(self.screen)
            if point == self.selected_mass_point:
                pygame.draw.circle(
                    self.screen, (255, 255, 0), point.pos.astype(int), 15, 2
                )
        pygame.display.update()

    # Dedicated slider callbacks:

    def _update_mass(self, value: float) -> None:
        """Update default mass and the selected mass point (if any)."""
        self.default_mass = value
        if self.selected_mass_point:
            self.selected_mass_point.mass = value

    def _update_stiffness(self, value: float) -> None:
        """Update default stiffness and the selected spring (if any)."""
        self.default_stiffness = value
        if self.selected_spring:
            self.selected_spring.stiffness = value

    def _update_rest_length(self, value: float) -> None:
        """Update default rest length and the selected spring (if any)."""
        self.default_rest_length = value
        if self.selected_spring:
            self.selected_spring.rest_length = value

    def _update_damping(self, value: float) -> None:
        """Update default damping and the selected spring (if any)."""
        self.default_damping = value
        if self.selected_spring:
            self.selected_spring.damping = value


def sandbox_game(screen: pygame.Surface) -> None:
    clock = pygame.time.Clock()
    game = SandboxGame(screen)
    running = True

    while running:
        clock.tick(FPS)
        if not game.process_events():
            running = False
        game.update()
        game.render()

    pygame.quit()


if __name__ == "__main__":
    sandbox_game(pygame.display.set_mode(WIN_SIZE))
