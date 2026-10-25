import pygame
from settings import *
from ui.hud import draw_hud


class Renderer:
    def __init__(self, screen):
        self.screen = screen

    def draw_text(self, text, x, y, color=DARK, font=FONT):
        self.screen.blit(font.render(str(text), True, color), (x, y))

    def draw_background(self, camera_x):
        self.screen.fill(SKY)
        for i in range(-1, 7):
            x = i * 260 - int(camera_x * 0.18) % 260
            pygame.draw.polygon(self.screen, MOUNTAIN, [(x, 520), (x + 125, 360 + (i % 3) * 30), (x + 260, 520)])
        for i in range(6):
            x = (i * 210 - int(camera_x * 0.3)) % (WIDTH + 180) - 80
            y = 90 + (i % 3) * 55
            for cx, cy, radius in [(x,y,17),(x+20,y-8,20),(x+40,y,15)]:
                pygame.draw.circle(self.screen, WHITE, (cx, cy), radius)

    def draw_world(self, world, camera_x):
        for segment in world.ground_segments:
            rect = segment.move(-camera_x, 0)
            if rect.right >= 0 and rect.left <= WIDTH:
                pygame.draw.rect(self.screen, DIRT, rect)
                pygame.draw.rect(self.screen, GRASS, (rect.x, rect.y, rect.width, 7))
        for platform in world.platforms:
            rect = platform.move(-camera_x, 0)
            if rect.right >= 0 and rect.left <= WIDTH:
                pygame.draw.rect(self.screen, PLATFORM_COLOR, rect)
                pygame.draw.rect(self.screen, GRASS, (rect.x, rect.y, rect.width, 4))
        for ladder in world.ladders:
            rect = ladder.move(-camera_x, 0)
            if rect.right < 0 or rect.left > WIDTH:
                continue
            pygame.draw.line(self.screen, (180,100,55), rect.topleft, (rect.left,rect.bottom), 3)
            pygame.draw.line(self.screen, (180,100,55), (rect.right,rect.top), (rect.right,rect.bottom), 3)
            for y in range(rect.top + 8, rect.bottom, 13):
                pygame.draw.line(self.screen, (180,100,55), (rect.left,y), (rect.right,y), 3)
        for item in world.decorations:
            rect = item.move(-camera_x, 0)
            if rect.right >= 0 and rect.left <= WIDTH:
                pygame.draw.rect(self.screen, DIRT, rect)
                pygame.draw.rect(self.screen, (91,57,36), rect, 2)
        for spike in world.spikes:
            x, y = spike["x"] - camera_x, spike["y"]
            for i in range(spike["count"]):
                sx = x + i * 13
                pygame.draw.polygon(self.screen, (220,45,65), [(sx,y),(sx+7,y-15),(sx+13,y)])
        for enemy in world.enemies:
            if not enemy.active:
                continue
            rect = enemy.rect.move(-camera_x, 0)
            if rect.right < 0 or rect.left > WIDTH:
                continue
            pygame.draw.rect(self.screen, enemy.data["color"], rect, border_radius=4)
            eye_y = rect.y + rect.height // 3
            pygame.draw.circle(self.screen, WHITE, (rect.x + rect.width//3, eye_y), 4)
            pygame.draw.circle(self.screen, WHITE, (rect.x + 2*rect.width//3, eye_y), 4)

    def draw_player(self, player, camera_x):
        rect = player.rect.move(-camera_x, 0)
        pygame.draw.rect(self.screen, BLUE, rect, border_radius=3)
        pygame.draw.rect(self.screen, (40,45,150), rect, 2, border_radius=3)

    def draw_hud(self, hp, score, message):
        draw_hud(self.screen, hp, score, message)

    def draw_quiz(self, quiz):
        if not quiz.active:
            return
        q = quiz.enemy.question
        remaining = quiz.remaining()
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((20,30,45,145))
        self.screen.blit(overlay, (0,0))
        panel = pygame.Rect(190,125,620,365)
        pygame.draw.rect(self.screen, CREAM, panel, border_radius=8)
        self.draw_text(q.get("subject","수학"),210,142,GRASS,SMALL)
        self.draw_text("문제 풀이",285,142,DARK,SMALL)
        self.draw_text(f"{remaining:.1f}s",740,142,RED if remaining < 10 else DARK,SMALL)
        bar = pygame.Rect(205,175,590,7)
        pygame.draw.rect(self.screen,GRAY,bar)
        ratio = remaining / max(1,quiz.duration)
        pygame.draw.rect(self.screen,GRASS if ratio > .3 else (220,130,50),(bar.x,bar.y,int(bar.width*ratio),bar.height))
        self.draw_text(q["q"],210,205,DARK,SMALL)
        for i, choice in enumerate(q["choices"]):
            option = pygame.Rect(205,245+i*48,590,39)
            selected = i == quiz.selected
            pygame.draw.rect(self.screen,(190,220,255) if selected else GRAY,option,border_radius=5)
            if selected:
                pygame.draw.rect(self.screen,(55,110,220),option,2,border_radius=5)
            self.draw_text(f"{i+1}. {choice}",220,option.y+8,DARK,SMALL)
        self.draw_text("↑/↓ 선택 · Enter 제출 · 마우스 클릭",210,450,DARK,SMALL)
