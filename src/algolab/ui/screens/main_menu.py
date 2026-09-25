import pygame

from algolab.ui.components.button import Button
from algolab.ui.components.surface import draw_pill
from algolab.ui.screens.screen import Screen
from algolab.ui.screens.screen_manager import ScreenManager
from algolab.ui.screens.asymptotic import AsymptoticScreen
from algolab.ui.screens.linked_list import LinkedListScreen
from algolab.ui.screens.queue import QueueScreen
from algolab.ui.screens.stack import StackScreen
from algolab.ui.screens.bst import BSTScreen
from algolab.ui.screens.heap import HeapScreen
from algolab.ui.screens.graph import GraphScreen
from algolab.ui.screens.hash_table import HashTableScreen
from algolab.ui.screens.sorting import SortingScreen
from algolab.ui.theme import Color, Font

CREDIT_TEXT = "Created by Amirmasoud Mohammadian"


class MainMenuScreen(Screen):
    """Main menu screen."""

    TOPICS = [
        ("Asymptotic Notation", True, "Big-O, growth curves"),
        ("Linked Lists", True, "Nodes and pointers"),
        ("Stacks", True, "LIFO push and pop"),
        ("Queues", True, "FIFO enqueue and dequeue"),
        ("Binary Search Trees", True, "Insert, search, delete"),
        ("Heaps", True, "Min and max heaps"),
        ("Graphs", True, "BFS, DFS, Dijkstra, Bellman-Ford"),
        ("Sorting", True, "Bubble, Merge, Quick, Heap, and more"),
        ("Hash Tables & Sets", True, "Chaining, probing, double hashing"),
    ]

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
        self.credit_font = Font.SMALL()

        self.buttons: list[Button] = []

        self._create_buttons()

    def _create_buttons(self) -> None:
        """Create one Button per topic, stacked in a single column."""

        self.buttons.clear()

        button_width = 420
        button_height = 55
        spacing = 15

        start_x = (self.surface.get_width() - button_width) // 2
        start_y = 165

        for index, (label, enabled, _) in enumerate(self.TOPICS):
            y = start_y + index * (button_height + spacing)

            self.buttons.append(
                Button(
                    pygame.Rect(start_x, y, button_width, button_height),
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
            6: GraphScreen,
            7: SortingScreen,
            8: HashTableScreen,
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
        self._render_topics()
        self._render_credit()

    def _render_header(self) -> None:
        title = self.title_font.render("AlgoLab", True, Color.TEXT_PRIMARY)
        title_rect = title.get_rect(center=(self.surface.get_width() // 2, 75))
        self.surface.blit(title, title_rect)

        subtitle = self.subtitle_font.render(
            "Data structure visualizations for the Data Structures course",
            True,
            Color.TEXT_SECONDARY,
        )
        subtitle_rect = subtitle.get_rect(
            center=(self.surface.get_width() // 2, 115)
        )
        self.surface.blit(subtitle, subtitle_rect)

    def _render_topics(self) -> None:
        for index, button in enumerate(self.buttons):
            _, enabled, caption = self.TOPICS[index]

            button.render(self.surface)

            if not enabled:
                pill_width = 96
                pill_height = 24

                pill_rect = pygame.Rect(
                    button.rect.right - pill_width - 14,
                    button.rect.centery - pill_height // 2,
                    pill_width,
                    pill_height,
                )

                draw_pill(
                    self.surface,
                    pill_rect,
                    Color.SURFACE_RAISED,
                    caption,
                    self.caption_font,
                    text_color=Color.TEXT_MUTED,
                )

    def _render_credit(self) -> None:
        """
        Small, unobtrusive credit line anchored to the bottom of the
        window. Kept muted (TEXT_MUTED) and small (SMALL font) so it
        reads as a footer rather than competing with the title or the
        topic buttons for attention.
        """

        credit = self.credit_font.render(CREDIT_TEXT, True, Color.TEXT_MUTED)

        credit_rect = credit.get_rect(
            centerx=self.surface.get_width() // 2,
            bottom=self.surface.get_height() - 12,
        )

        self.surface.blit(credit, credit_rect)