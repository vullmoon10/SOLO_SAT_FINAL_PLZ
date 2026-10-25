import pygame
from settings import MOVE_SPEED, GRAVITY, JUMP_POWER, MAX_FALL_SPEED, GROUND_Y


class Player:
    def __init__(self, x=60, y=450, cheats=None):
        self.rect = pygame.Rect(x, y, 22, 30)
        self.vy = 0.0
        self.on_ground = False
        self.climbing = False
        self.cheats = cheats or {}

    def update(self, keys, world):
        speed = 500 if self.cheats.get("superspeed") else MOVE_SPEED
        dx = int(bool(keys[pygame.K_d] or keys[pygame.K_RIGHT])) * speed
        dx -= int(bool(keys[pygame.K_a] or keys[pygame.K_LEFT])) * speed
        self.rect.x += dx

        # 사다리는 플레이어의 발 위치까지 포함해 판정하고, 사다리 밖으로 나가면 중력을 복구한다.
        ladder = next((item for item in world.ladders
                       if self.rect.centerx >= item.left - 8
                       and self.rect.centerx <= item.right + 8
                       and self.rect.bottom >= item.top
                       and self.rect.top <= item.bottom), None)
        climb_input = int(bool(keys[pygame.K_s] or keys[pygame.K_DOWN])) - int(bool(keys[pygame.K_w] or keys[pygame.K_UP]))
        self.climbing = ladder is not None and climb_input != 0

        previous = self.rect.copy()
        if self.climbing:
            self.rect.y += climb_input * speed
            self.rect.top = max(self.rect.top, ladder.top - self.rect.height + 2)
            self.rect.bottom = min(self.rect.bottom, ladder.bottom)
            self.vy = 0
        else:
            self.vy = min(self.vy + GRAVITY, MAX_FALL_SPEED)
            self.rect.y += int(self.vy)

        self.on_ground = False
        if not self.climbing and self.vy >= 0:
            for surface in world.ground_segments + world.platforms:
                overlap = self.rect.right > surface.left and self.rect.left < surface.right
                crossed_top = previous.bottom <= surface.top and self.rect.bottom >= surface.top
                # 사다리에서 내려와 이미 발판 높이 안쪽에 있는 경우도 착지시킨다.
                ladder_exit_landing = (previous.bottom <= surface.top + 3 and self.rect.bottom >= surface.top
                                       and previous.top < surface.top and self.rect.bottom <= surface.top + 16)
                if overlap and (crossed_top or ladder_exit_landing):
                    self.rect.bottom = surface.top
                    self.vy = 0
                    self.on_ground = True
                    break

        # 월드 가장자리에서 플레이어가 무한히 화면 밖으로 걸어나가지 않게 한다.
        self.rect.x = max(0, self.rect.x)

    def jump(self):
        if self.on_ground:
            self.vy = -20 if self.cheats.get("superjump") else JUMP_POWER
            self.on_ground = False
            self.climbing = False

    def reset_position(self):
        self.rect.x, self.rect.y, self.vy = 60, 400, 0
        self.on_ground = False
        self.climbing = False
