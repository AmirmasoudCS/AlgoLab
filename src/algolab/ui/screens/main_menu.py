import pygame

from algolab.ui.screens.screen import Screen
from algolab.ui.screens.screen_manager import ScreenManager
from algolab.ui.screens.asymptotic import AsymptoticScreen


class MainMenuScreen(Screen):
    """Main menu screen."""

    def __init__(
        self,
        surface: pygame.Surface,
        screen_manager: ScreenManager,
    ) -> None:
        super().__init__(surface)

        self.screen_manager = screen_manager

        self.font = pygame.font.Font(None, 36)
        self.title_font = pygame.font.Font(None, 64)

        self.topic_buttons = [
            ("Asymptotic Notation", True),
            ("Linked Lists", False),
            ("Stacks & Queues", False),
            ("Trees & Heaps", False),
            ("Graphs", False),
            ("Sorting", False),
            ("Hash Tables & Sets", False),
        ]

        self.button_rects: list[tuple[pygame.Rect, bool]] = []

        self._create_buttons()

    def _create_buttons(self) -> None:
        """Create the rectangles used by topic buttons."""

        self.button_rects.clear()

        button_width = 400
        button_height = 55
        spacing = 15

        start_x = (self.surface.get_width() - button_width) // 2
        start_y = 160

        for index, (_, enabled) in enumerate(self.topic_buttons):
            y = start_y + index * (button_height + spacing)

            rect = pygame.Rect(
                start_x,
                y,
                button_width,
                button_height,
            )

            self.button_rects.append((rect, enabled))

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type != pygame.MOUSEBUTTONDOWN:
            return

        if event.button != 1:
            return

        for index, (rect, enabled) in enumerate(self.button_rects):
            if not enabled or not rect.collidepoint(event.pos):
                continue

            self._select_topic(index)
            break

    def _select_topic(self, index: int) -> None:
        """Open the selected topic."""

        if index == 0:
            self.screen_manager.set_screen(
                AsymptoticScreen(self.surface)
            )

    def update(self, dt: float) -> None:
        pass

    def render(self) -> None:
        self.surface.fill((30, 30, 30))

        title = self.title_font.render(
            "AlgoLab",
            True,
            (255, 255, 255),
        )

        title_rect = title.get_rect(
            center=(self.surface.get_width() // 2, 80)
        )

        self.surface.blit(title, title_rect)

        mouse_position = pygame.mouse.get_pos()

        for index, (rect, enabled) in enumerate(self.button_rects):
            label, _ = self.topic_buttons[index]

            if enabled and rect.collidepoint(mouse_position):
                background = (70, 70, 70)
            elif enabled:
                background = (50, 50, 50)
            else:
                background = (40, 40, 40)

            pygame.draw.rect(
                self.surface,
                background,
                rect,
                border_radius=8,
            )

            text_color = (
                (255, 255, 255)
                if enabled
                else (120, 120, 120)
            )

            text = self.font.render(
                label,
                True,
                text_color,
            )

            text_rect = text.get_rect(
                center=rect.center
            )

            self.surface.blit(text, text_rect)