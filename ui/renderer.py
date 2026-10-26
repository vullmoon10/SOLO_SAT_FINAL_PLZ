import pygame
from settings import *
from ui.hud import draw_hud


class Renderer:  # 월드·플레이어·퀴즈 화면 렌더링을 담당한다.
    def __init__(self, screen):
        self.screen = screen  # 렌더링 대상 화면

    def draw_text(self, text, x, y, color=DARK, font=FONT):  # 지정한 위치와 스타일로 텍스트를 그린다.
        self.screen.blit(font.render(str(text), True, color), (x, y))

    def draw_background(self, camera_x):  # 카메라 위치에 맞춘 배경 산과 구름을 그린다.
        self.screen.fill(SKY)
        for i in range(-1, 7):
            x = i * 260 - int(camera_x * 0.18) % 260  # 카메라 움직임을 반영한 산의 가로 위치
            pygame.draw.polygon(self.screen, MOUNTAIN, [(x, 520), (x + 125, 360 + (i % 3) * 30), (x + 260, 520)])
        for i in range(6):
            x = (i * 210 - int(camera_x * 0.3)) % (WIDTH + 180) - 80  # 화면에 반복되는 구름의 가로 위치
            y = 90 + (i % 3) * 55  # 구름의 세로 위치
            for cx, cy, radius in [(x,y,17),(x+20,y-8,20),(x+40,y,15)]:
                pygame.draw.circle(self.screen, WHITE, (cx, cy), radius)

    def draw_world(self, world, camera_x):  # 월드 지형·장애물·적을 화면에 그린다.
        for segment in world.ground_segments:
            rect = segment.move(-camera_x, 0)  # 카메라 좌표를 반영한 지면 영역
            if rect.right >= 0 and rect.left <= WIDTH:  # 화면에 보이는 지면만 렌더링한다.
                pygame.draw.rect(self.screen, DIRT, rect)
                pygame.draw.rect(self.screen, GRASS, (rect.x, rect.y, rect.width, 7))
        for platform in world.platforms:
            rect = platform.move(-camera_x, 0)  # 카메라 좌표를 반영한 발판 영역
            if rect.right >= 0 and rect.left <= WIDTH:  # 화면에 보이는 발판만 렌더링한다.
                pygame.draw.rect(self.screen, PLATFORM_COLOR, rect)
                pygame.draw.rect(self.screen, GRASS, (rect.x, rect.y, rect.width, 4))
        for ladder in world.ladders:
            rect = ladder.move(-camera_x, 0)  # 카메라 좌표를 반영한 사다리 영역
            if rect.right < 0 or rect.left > WIDTH:  # 화면 밖 사다리는 그리지 않는다.
                continue
            pygame.draw.line(self.screen, (180,100,55), rect.topleft, (rect.left,rect.bottom), 3)
            pygame.draw.line(self.screen, (180,100,55), (rect.right,rect.top), (rect.right,rect.bottom), 3)
            for y in range(rect.top + 8, rect.bottom, 13):
                pygame.draw.line(self.screen, (180,100,55), (rect.left,y), (rect.right,y), 3)
        for item in world.decorations:
            rect = item.move(-camera_x, 0)  # 카메라 좌표를 반영한 장식 영역
            if rect.right >= 0 and rect.left <= WIDTH:  # 화면에 보이는 장식만 렌더링한다.
                pygame.draw.rect(self.screen, DIRT, rect)
                pygame.draw.rect(self.screen, (91,57,36), rect, 2)
        for spike in world.spikes:
            x, y = spike["x"] - camera_x, spike["y"]  # 카메라를 반영한 가시 시작 좌표
            for i in range(spike["count"]):
                sx = x + i * 13  # 개별 가시의 가로 좌표
                pygame.draw.polygon(self.screen, (220,45,65), [(sx,y),(sx+7,y-15),(sx+13,y)])
        for enemy in world.enemies:
            if not enemy.active:  # 처치된 적은 렌더링하지 않는다.
                continue
            rect = enemy.rect.move(-camera_x, 0)  # 카메라 좌표를 반영한 적 영역
            if rect.right < 0 or rect.left > WIDTH:  # 화면 밖 적은 그리지 않는다.
                continue
            pygame.draw.rect(self.screen, enemy.data["color"], rect, border_radius=4)
            eye_y = rect.y + rect.height // 3  # 적 눈의 세로 위치
            pygame.draw.circle(self.screen, WHITE, (rect.x + rect.width//3, eye_y), 4)
            pygame.draw.circle(self.screen, WHITE, (rect.x + 2*rect.width//3, eye_y), 4)

    def draw_player(self, player, camera_x):  # 카메라 위치를 반영해 플레이어를 그린다.
        rect = player.rect.move(-camera_x, 0)  # 화면 좌표로 변환한 플레이어 영역
        pygame.draw.rect(self.screen, BLUE, rect, border_radius=3)
        pygame.draw.rect(self.screen, (40,45,150), rect, 2, border_radius=3)

    def draw_hud(self, hp, score, message):  # 체력·점수·알림 UI를 렌더링한다.
        draw_hud(self.screen, hp, score, message)

    def draw_quiz(self, quiz):  # 활성 퀴즈와 답변 선택 UI를 그린다.
        if not quiz.active:  # 진행 중인 퀴즈가 없으면 그리기를 생략한다.
            return
        q = quiz.enemy.question  # 현재 출제 중인 문제 데이터
        remaining = quiz.remaining()  # 문제 제한 시간의 남은 초
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)  # 배경을 어둡게 덮는 오버레이
        overlay.fill((20,30,45,145))
        self.screen.blit(overlay, (0,0))
        panel = pygame.Rect(190,125,620,365)  # 퀴즈 대화상자 영역
        pygame.draw.rect(self.screen, CREAM, panel, border_radius=8)
        self.draw_text(q.get("subject","수학"),210,142,GRASS,SMALL)
        self.draw_text("문제 풀이",285,142,DARK,SMALL)
        self.draw_text(f"{remaining:.1f}s",740,142,RED if remaining < 10 else DARK,SMALL)
        bar = pygame.Rect(205,175,590,7)  # 남은 시간을 표시하는 진행 막대
        pygame.draw.rect(self.screen,GRAY,bar)
        ratio = remaining / max(1,quiz.duration)  # 제한 시간 대비 남은 시간 비율
        pygame.draw.rect(self.screen,GRASS if ratio > .3 else (220,130,50),(bar.x,bar.y,int(bar.width*ratio),bar.height))
        self.draw_text(q["q"],210,205,DARK,SMALL)
        for i, choice in enumerate(q["choices"]):
            option = pygame.Rect(205,245+i*48,590,39)  # 선택지 버튼 영역
            selected = i == quiz.selected  # 현재 선택된 답인지 여부
            pygame.draw.rect(self.screen,(190,220,255) if selected else GRAY,option,border_radius=5)
            if selected:
                pygame.draw.rect(self.screen,(55,110,220),option,2,border_radius=5)
            self.draw_text(f"{i+1}. {choice}",220,option.y+8,DARK,SMALL)
        self.draw_text("↑/↓ 선택 · Enter 제출 · 마우스 클릭",210,450,DARK,SMALL)
