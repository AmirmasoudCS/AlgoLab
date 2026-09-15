import pygame

from algolab.ui.components.button import Button
from algolab.ui.screens.screen import Screen
from algolab.ui.screens.screen_manager import ScreenManager
from algolab.ui.screens.asymptotic import AsymptoticScreen
from algolab.ui.screens.linked_list import LinkedListScreen
from algolab.ui.screens.queue import QueueScreen
from algolab.ui.screens.stack import StackScreen
from algolab.ui.screens.bst import BSTScreen
from algolab.ui.screens.heap import HeapScreen
from algolab.ui.theme import Color, Font


class MainMenuScreen(Screen):
    """Main menu screen."""

    TOPICS = [
        ("Asymptotic Notation", True, "Big-O, growth curves"),
        ("Linked Lists", True, "Nodes and pointers"),
        ("Stacks", True, "LIFO push and pop"),
        ("Queues", True, "FIFO enqueue and dequeue"),
        ("Binary Search Trees", True, "Insert, search, delete"),
        ("Heaps", True, "Min and max heaps"),
        ("Graphs", False, "Coming soon"),
        ("Sorting", False, "Coming soon"),
        ("Hash Tables & Sets", False, "Coming soon"),
    ]

    COLUMNS = 3

    def __init__(
        self,
        surface: pygame.Surface,
        screen_manager: ScreenManager,
    ) -> None:
        # The main menu is the root screen, so it doesn't get a back
        # button of its own.
        super().__init__(surface, on_back=None)

        self.screen_manager = screen_manager

        self.title_font = Font.get(64, bold=True)
        self.subtitle_font = Font.BODY()
        self.card_font = Font.get(24, bold=True)
        self.caption_font = Font.SMALL()

        self.buttons: list[Button] = []

        self._create_buttons()

    def _create_buttons(self) -> None:
        """Create one Button per topic, arranged in a card grid."""

        self.buttons.clear()

        card_width = 340
        card_height = 120
        gap_x = 30
        gap_y = 24

        grid_width = self.COLUMNS * card_width + (self.COLUMNS - 1) * gap_x
        start_x = (self.surface.get_width() - grid_width) // 2
        start_y = 190

        for index, (label, enabled, _) in enumerate(self.TOPICS):
            row = index // self.COLUMNS
            column = index % self.COLUMNS

            x = start_x + column * (card_width + gap_x)
            y = start_y + row * (card_height + gap_y)

            self.buttons.append(
                Button(
                    pygame.Rect(x, y, card_width, card_height),
                    label,
                    enabled=enabled,
                    variant="primary",
                )
            )

    def handle_event(self, event: pygame.event.Event) -> None:
        for index, button in enumerate(self.buttons):
            if button.handle_event(event):
                self._select_topic(index)

    def _select_topic(self, index: int) -> None:
        """Open the selected topic, wiring it back to a fresh menu."""

        def go_back() -> None:
            self.screen_manager.set_screen(
                MainMenuScreen(self.surface, self.screen_manager)
            )

        screen_classes = {
            0: AsymptoticScreen,
            1: LinkedListScreen,
            2: StackScreen,
            3: QueueScreen,
            4: BSTScreen,
            5: HeapScreen,
        }

        screen_class = screen_classes.get(index)

        if screen_class is None:
            return

        self.screen_manager.set_screen(
            screen_class(self.surface, on_back=go_back)
        )

    def update(self, dt: float) -> None:
        for button in self.buttons:
            button.update(dt)

    def render(self) -> None:
        self.surface.fill(Color.BG)

        self._render_header()
        self._render_cards()

    def _render_header(self) -> None:
        title = self.title_font.render("AlgoLab", True, Color.TEXT_PRIMARY)
        title_rect = title.get_rect(center=(self.surface.get_width() // 2, 85))
        self.surface.blit(title, title_rect)

        subtitle = self.subtitle_font.render(
            "Data structure visualizations for the Data Structures course",
            True,
            Color.TEXT_SECONDARY,
        )
        subtitle_rect = subtitle.get_rect(
            center=(self.surface.get_width() // 2, 130)
        )
        self.surface.blit(subtitle, subtitle_rect)

    def _render_cards(self) -> None:
        for index, button in enumerate(self.buttons):
            _, enabled, caption = self.TOPICS[index]

            button.render(self.surface)

            caption_color = Color.TEXT_SECONDARY if enabled else Color.TEXT_MUTED

            caption_surface = self.caption_font.render(caption, True, caption_color)
            caption_rect = caption_surface.get_rect(
                centerx=button.rect.centerx,
                top=button.rect.centery + 18,
            )

            self.surface.blit(caption_surface, caption_rect)