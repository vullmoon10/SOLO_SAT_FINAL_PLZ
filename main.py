import pygame
from settings import WIDTH, HEIGHT, TITLE
from core.game import Game
from ui.menu import Menu


def main():  # 게임 초기화부터 메뉴와 플레이 흐름을 실행한다.
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))  # 기본 게임 화면을 만든다.
    pygame.display.set_caption(TITLE)
    try:
        while True:
            action = Menu(screen).run()  # 메뉴에서 선택한 동작을 받는다.
            screen = pygame.display.get_surface()  # 메뉴가 변경한 현재 화면을 가져온다.
            if action == "quit":  # 종료 선택 시 메뉴 반복을 끝낸다.
                break
            if action == "new_game":  # 새 게임 선택 시 게임 루프를 실행한다.
                Game(screen).run()
                screen = pygame.display.get_surface()  # 게임 종료 후 현재 화면을 갱신한다.
    finally:
        pygame.quit()


if __name__ == "__main__":  # 직접 실행할 때만 게임을 시작한다.
    main()
