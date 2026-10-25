import pygame
from systems.quiz import get_random_question

ENEMY_TYPES = {
    "basic": {"color": (210, 65, 65), "size": (30, 30), "difficulty": "easy", "hp": 2, "score": 100},
    "advanced": {"color": (130, 90, 65), "size": (36, 36), "difficulty": "medium", "hp": 4, "score": 200},
}


class Enemy:
    def __init__(self, x, ground_y, enemy_type="basic"):
        self.enemy_type = enemy_type
        self.data = ENEMY_TYPES[enemy_type]
        width, height = self.data["size"]
        self.rect = pygame.Rect(x, ground_y - height, width, height)
        self.hp = self.data["hp"]
        self.active = True
        self.question = get_random_question(self.data["difficulty"])

    def defeat(self):
        self.hp -= 1
        if self.hp <= 0:
            self.active = False
            return True
        self.question = get_random_question(self.data["difficulty"])
        return False
