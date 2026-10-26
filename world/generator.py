import random
import pygame
from settings import WIDTH, HEIGHT, GROUND_Y
from world.terrain import Terrain
from entities.enemies import Enemy


class World(Terrain):  # 지형을 무한 생성하고 오래된 구간을 정리한다.
    def __init__(self):
        super().__init__()
        self.generate_chunk(0, 12)

    def generate_chunk(self, start_x, count=5):  # 시작 좌표부터 무작위 지형 구간을 생성한다.
        x = start_x  # 현재 지형 생성 기준 좌표
        for _ in range(count):
            width = random.randint(190, 290)  # 이번 지면 구간의 폭
            self.ground_segments.append(pygame.Rect(x, GROUND_Y, width, HEIGHT - GROUND_Y))
            if random.random() < 0.45:  # 일정 확률로 지면 장식을 배치한다.
                bw, bh = random.choice([28, 36, 48]), random.choice([35, 50, 65])  # 장식의 폭과 높이
                bx = x + random.randint(40, max(41, width - bw))  # 장식의 가로 좌표
                self.decorations.append(pygame.Rect(bx, GROUND_Y - bh, bw, bh))
            if random.random() < 0.35:  # 일정 확률로 가시 장애물을 배치한다.
                self.spikes.append({"x": x + random.randint(40, max(41, width - 70)), "y": GROUND_Y, "count": random.randint(3, 5)})
            if random.random() < 0.9:  # 대부분의 구간에 높은 발판을 생성한다.
                pw = random.randint(100, min(150, width - 40))  # 발판 폭
                px = x + random.randint(20, width - pw - 20)  # 발판 가로 좌표
                py = random.randint(350, 455)  # 발판 세로 좌표
                self.platforms.append(pygame.Rect(px, py, pw, 12))
                if random.random() < 0.7:  # 발판과 지면을 잇는 사다리를 추가한다.
                    self.ladders.append(pygame.Rect(px + pw // 2 - 11, py, 22, GROUND_Y - py + 2))
                if random.random() < 0.6:  # 일정 확률로 발판 위에 적을 배치한다.
                    self.add_enemy(px + random.randint(15, max(16, pw - 35)), py)
            if random.random() < 0.4:  # 일정 확률로 지면 위에 적을 배치한다.
                self.add_enemy(x + random.randint(40, max(41, width - 35)), GROUND_Y)
            x += width
        self.world_end = x  # 새로 생성된 월드의 마지막 좌표를 기록한다.

    def add_enemy(self, x, ground_y):  # 지정 위치에 기본 적을 추가한다.
        self.enemies.append(Enemy(x, ground_y))

    def update_generation(self, player_x):  # 플레이어 진행에 맞춰 지형을 생성하고 뒤쪽을 정리한다.
        if self.world_end < player_x + WIDTH + 700:  # 월드 끝이 가까우면 다음 구간을 생성한다.
            self.generate_chunk(self.world_end + random.randint(20, 60), 5)
        cutoff = player_x - WIDTH - 300  # 화면 뒤편에서 제거할 기준 좌표
        self.platforms = [o for o in self.platforms if o.right > cutoff]
        self.ground_segments = [o for o in self.ground_segments if o.right > cutoff]
        self.ladders = [o for o in self.ladders if o.right > cutoff]
        self.spikes = [s for s in self.spikes if s["x"] + s["count"] * 13 > cutoff]
        self.decorations = [o for o in self.decorations if o.right > cutoff]
        self.enemies = [o for o in self.enemies if o.rect.right > cutoff]
