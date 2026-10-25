import pygame
from settings import WIDTH, HEIGHT, SKY, MOUNTAIN, GRASS, WHITE, DARK, CREAM, BLUE, YELLOW, GRAY


class Menu:
    """SOLO SAT 메인 메뉴와 하위 메뉴."""
    def __init__(self, screen):
        self.screen = screen
        self.clock = pygame.time.Clock()
        self.page = "main"
        self.selected = 0
        self.notice = ""
        self.notice_until = 0
        self.buttons = []
        self.running = True

        self.font = pygame.font.SysFont("malgungothic", 22)
        self.small = pygame.font.SysFont("malgungothic", 16)
        self.title_font = pygame.font.SysFont("malgungothic", 52, bold=True)
        self.subtitle_font = pygame.font.SysFont("malgungothic", 20)

    def _text(self, text, pos, font, color, center=True):
        surf = font.render(str(text), True, color)
        rect = surf.get_rect(center=pos) if center else surf.get_rect(topleft=pos)
        self.screen.blit(surf, rect)
        return rect

    def _background(self):
        self.screen.fill(SKY)
        # 먼 산과 언덕
        for i in range(6):
            x = i * 220 - 70
            pygame.draw.polygon(self.screen, MOUNTAIN,
                                [(x, 430), (x + 110, 245 + (i % 3) * 28), (x + 250, 430)])
        pygame.draw.rect(self.screen, (132, 183, 116), (0, 420, WIDTH, HEIGHT - 420))
        pygame.draw.rect(self.screen, (87, 151, 83), (0, 420, WIDTH, 8))
        # 작은 플랫폼 장식
        for x, y, w in [(65, 365, 125), (780, 330, 145), (690, 390, 85)]:
            pygame.draw.rect(self.screen, (103, 128, 95), (x, y, w, 10), border_radius=3)
            pygame.draw.rect(self.screen, GRASS, (x, y, w, 4), border_radius=2)
        # 중앙 패널
        panel = pygame.Surface((520, 500), pygame.SRCALPHA)
        panel.fill((17, 31, 49, 224))
        self.screen.blit(panel, (240, 45))
        pygame.draw.rect(self.screen, (255, 255, 255, 55), (240, 45, 520, 500), 2, border_radius=12)

    def _button(self, label, y, index, subtitle=None):
        rect = pygame.Rect(330, y, 340, 48 if subtitle is None else 56)
        active = index == self.selected
        fill = (255, 220, 70) if active else (238, 242, 247)
        ink = (30, 43, 57) if active else (47, 62, 78)
        pygame.draw.rect(self.screen, fill, rect, border_radius=8)
        if active:
            pygame.draw.rect(self.screen, WHITE, rect, 2, border_radius=8)
        if subtitle:
            self._text(label, (rect.centerx, rect.y + 18), self.font, ink)
            self._text(subtitle, (rect.centerx, rect.y + 40), self.small, ink)
        else:
            self._text(label, rect.center, self.font, ink)
        self.buttons.append((rect, index))

    def _draw_main(self):
        self._text("나 혼자만 1등급", (500, 112), self.title_font, WHITE)
        self._text("SOLO SAT", (500, 163), self.subtitle_font, YELLOW)
        self._text("STUDY · SURVIVE · RANK UP", (500, 193), self.small, (204, 218, 232))
        self.buttons = []
        self._button("새 게임", 235, 0, "새로운 도전을 시작한다")
        self._button("불러오기", 305, 1, "저장 슬롯 선택")
        self._button("크레딧", 375, 2)
        self._button("종료", 435, 3)
        self._text("↑ / ↓ 선택   ·   Enter 실행   ·   마우스 클릭", (500, 510), self.small, (211, 220, 230))

    def _draw_load(self):
        self._text("게임 불러오기", (500, 112), self.title_font, WHITE)
        self._text("저장 슬롯을 선택해", (500, 166), self.subtitle_font, (211, 220, 230))
        self.buttons = []
        for i, slot in enumerate(("SLOT 1", "SLOT 2", "SLOT 3")):
            self._button(slot, 230 + i * 75, i, "저장 데이터 없음")
        self._button("뒤로", 465, 3)
        self._text("저장 기능은 게임 내 저장 연동 후 사용할 수 있어", (500, 525), self.small, YELLOW)

    def _draw_credits(self):
        self._text("크레딧", (500, 130), self.title_font, WHITE)
        self._text("SOLO SAT · 나 혼자만 1등급", (500, 220), self.font, YELLOW)
        self._text("2026 VIAUS 프로젝트", (500, 265), self.subtitle_font, WHITE)
        self._text("Pygame 기반 학습형 플랫폼 게임 프로토타입", (500, 305), self.small, (211, 220, 230))
        self._text("기획 · 개발: SOLO SAT 프로젝트", (500, 340), self.small, (211, 220, 230))
        self.buttons = []
        self._button("뒤로", 425, 0)

    def draw(self):
        self._background()
        if self.page == "main":
            self._draw_main()
        elif self.page == "load":
            self._draw_load()
        else:
            self._draw_credits()
        if self.notice and pygame.time.get_ticks() < self.notice_until:
            self._text(self.notice, (500, 480), self.small, YELLOW)

    def _activate(self, index):
        if self.page == "main":
            if index == 0:
                return "new_game"
            if index == 1:
                self.page, self.selected = "load", 0
            elif index == 2:
                self.page, self.selected = "credits", 0
            elif index == 3:
                return "quit"
        elif self.page == "load":
            if index == 3:
                self.page, self.selected = "main", 0
            else:
                self.notice = "이 슬롯에는 저장 데이터가 없어. 새 게임을 시작해줘."
                self.notice_until = pygame.time.get_ticks() + 2500
        else:
            self.page, self.selected = "main", 0
        return None

    def run(self):
        while self.running:
            self.clock.tick(60)
            self.draw()
            pygame.display.flip()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return "quit"
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        if self.page == "main":
                            return "quit"
                        self.page, self.selected = "main", 0
                    elif event.key in (pygame.K_UP, pygame.K_w):
                        self.selected = max(0, self.selected - 1)
                    elif event.key in (pygame.K_DOWN, pygame.K_s):
                        max_index = 3 if self.page in ("main", "load") else 0
                        self.selected = min(max_index, self.selected + 1)
                    elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                        result = self._activate(self.selected)
                        if result:
                            return result
                elif event.type == pygame.MOUSEMOTION:
                    for rect, index in self.buttons:
                        if rect.collidepoint(event.pos):
                            self.selected = index
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    for rect, index in self.buttons:
                        if rect.collidepoint(event.pos):
                            result = self._activate(index)
                            if result:
                                return result
        return "quit"
