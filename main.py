import pygame
from settings import WIDTH, HEIGHT, TITLE
from core.game import Game
from ui.menu import Menu


def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption(TITLE)
    try:
        while True:
            action = Menu(screen).run()
            if action == "quit":
                break
            if action == "new_game":
                Game(screen).run()
    finally:
        pygame.quit()


if __name__ == "__main__":
    main()
