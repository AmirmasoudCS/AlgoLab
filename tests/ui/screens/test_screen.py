import pygame

from algolab.ui.screens.screen import Screen


class DummyScreen(Screen):
    def handle_event(self, event):
        pass

    def update(self, dt):
        pass

    def render(self):
        pass


def test_screen_stores_surface():
    surface = pygame.Surface((800, 600))

    screen = DummyScreen(surface)

    assert screen.surface is surface