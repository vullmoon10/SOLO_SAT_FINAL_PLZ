import pygame
import os

WIDTH, HEIGHT, FPS = 1000, 600, 60
TITLE = "SOLO SAT"
MOVE_SPEED, GRAVITY, JUMP_POWER, MAX_FALL_SPEED = 5, 0.5, -10, 10
MAX_HP, CORRECT_SCORE, WRONG_DAMAGE, QUESTION_TIME = 100, 100, 10, 30
SKY = (126, 196, 235)
MOUNTAIN = (150, 176, 196)
GRASS = (81, 170, 89)
PLATFORM_COLOR = (112, 133, 92)
DIRT = (132, 86, 53)
BLUE = (65, 75, 225)
RED = (210, 65, 65)
WHITE = (255, 255, 255)
DARK = (39, 54, 67)
CREAM = (250, 249, 239)
GRAY = (232, 232, 240)
YELLOW = (255, 220, 70)
GROUND_Y = 520

pygame.font.init()
FONT = pygame.font.SysFont("malgungothic", 22)
SMALL = pygame.font.SysFont("malgungothic", 16)
TITLE_FONT = pygame.font.SysFont("malgungothic", 27)
BIG = pygame.font.SysFont("malgungothic", 34)


def choose_cheat():
    """치트는 SOLO_SAT_CHEAT 환경변수로 선택한다. 기본값은 일반 모드."""
    cheats = {
        "1": {"no_damage": True},
        "2": {"superspeed": True},
        "3": {"superjump": True},
        "4": {"superspeed": True, "superjump": True},
        "5": {"no_damage": True, "superspeed": True, "superjump": True},
    }
    return cheats.get(os.getenv("SOLO_SAT_CHEAT", "").strip(), {})