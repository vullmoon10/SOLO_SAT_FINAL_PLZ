import pygame
from settings import WIDTH, HEIGHT, SKY, MOUNTAIN, GRASS, WHITE, DARK, CREAM, BLUE, YELLOW, GRAY
from core.display import toggle_fullscreen


class Menu:  # 메인·불러오기·크레딧 메뉴 화면을 관리
    """SOLO SAT 메인 메뉴와 하위 메뉴."""
    def __init__(self, screen):  # 메뉴 화면과 초기 상태를 준비
        self.screen = screen  # 메뉴를 그릴 화면
        self.clock = pygame.time.Clock()  # 메뉴 프레임 속도 조절 시계
        self.page = "main"  # 현재 표시할 메뉴 페이지
        self.selected = 0  # 현재 선택된 버튼 인덱스
        self.notice = ""  # 화면 하단 알림 문구
        self.notice_until = 0  # 알림 표시 종료 시각
        self.buttons = []  # 현재 페이지 버튼의 위치와 인덱스
        self.running = True  # 메뉴 반복 실행 여부

        self.font = pygame.font.SysFont("malgungothic", 22)  # 기본 메뉴 글꼴
        self.small = pygame.font.SysFont("malgungothic", 16)  # 보조 안내 글꼴
        self.title_font = pygame.font.SysFont("malgungothic", 52, bold=True)  # 메뉴 제목 글꼴
        self.subtitle_font = pygame.font.SysFont("malgungothic", 20)  # 부제목 글꼴

    def _text(self, text, pos, font, color, center=True):  # 지정 위치와 스타일로 메뉴 문구를 그리기
        surf = font.render(str(text), True, color)  # 출력할 글자 표면
        rect = surf.get_rect(center=pos) if center else surf.get_rect(topleft=pos)  # 정렬 기준에 맞춘 문구 영역
        self.screen.blit(surf, rect)
        return rect

    def _background(self):  # 메뉴 배경과 반투명 패널을 그리기
        self.screen.fill(SKY)
        # 먼 산과 언덕
        for i in range(6):
            x = i * 220 - 70  # 산 봉우리의 가로 위치
            pygame.draw.polygon(self.screen, MOUNTAIN,
                                [(x, 430), (x + 110, 245 + (i % 3) * 28), (x + 250, 430)])
        pygame.draw.rect(self.screen, (132, 183, 116), (0, 420, WIDTH, HEIGHT - 420))
        pygame.draw.rect(self.screen, (87, 151, 83), (0, 420, WIDTH, 8))
        # 작은 플랫폼 장식
        for x, y, w in [(65, 365, 125), (780, 330, 145), (690, 390, 85)]:
            pygame.draw.rect(self.screen, (103, 128, 95), (x, y, w, 10), border_radius=3)
            pygame.draw.rect(self.screen, GRASS, (x, y, w, 4), border_radius=2)
        # 중앙 패널
        panel = pygame.Surface((520, 500), pygame.SRCALPHA)  # 메뉴 중앙 반투명 패널
        panel.fill((17, 31, 49, 224))
        self.screen.blit(panel, (240, 45))
        pygame.draw.rect(self.screen, (255, 255, 255, 55), (240, 45, 520, 500), 2, border_radius=12)

    def _button(self, label, y, index, subtitle=None):  # 버튼과 선택 표시를 그려 입력 목록에 등록
        rect = pygame.Rect(330, y, 340, 48 if subtitle is None else 56)  # 버튼 화면 영역
        active = index == self.selected  # 현재 선택된 버튼인지 여부
        fill = (255, 220, 70) if active else (238, 242, 247)  # 선택 상태에 따른 버튼 배경색
        ink = (30, 43, 57) if active else (47, 62, 78)  # 선택 상태에 따른 글자색
        pygame.draw.rect(self.screen, fill, rect, border_radius=8)
        if active:  # 선택된 버튼에 테두리를 표시
            pygame.draw.rect(self.screen, WHITE, rect, 2, border_radius=8)
        if subtitle:  # 부제목이 있으면 두 줄로 표시
            self._text(label, (rect.centerx, rect.y + 18), self.font, ink)
            self._text(subtitle, (rect.centerx, rect.y + 40), self.small, ink)
        else:
            self._text(label, rect.center, self.font, ink)
        self.buttons.append((rect, index))

    def _draw_main(self):  # 메인 메뉴 제목과 버튼을 그리기
        self._text("나 혼자만 1등급", (500, 112), self.title_font, WHITE)
        self._text("SOLO SAT", (500, 163), self.subtitle_font, YELLOW)
        self._text("STUDY · SURVIVE · RANK UP", (500, 193), self.small, (204, 218, 232))
        self.buttons = []  # 메인 페이지 버튼 목록을 새로 구성
        self._button("새 게임", 235, 0, "새로운 도전을 시작한다")
        self._button("불러오기", 305, 1, "저장 슬롯 선택")
        self._button("랭킹", 375, 2)
        self._button("종료", 435, 3)
        self._text("↑ / ↓ 선택   ·   Enter 실행   ·   마우스 클릭", (500, 510), self.small, (211, 220, 230))

    def _draw_load(self):  # 저장 슬롯 선택 화면을 그리기
        self._text("게임 불러오기", (500, 112), self.title_font, WHITE)
        self._text("저장 슬롯을 선택해", (500, 166), self.subtitle_font, (211, 220, 230))
        self.buttons = []  # 저장 슬롯 페이지 버튼 목록을 새로 구성
        for i, slot in enumerate(("SLOT 1", "SLOT 2", "SLOT 3")):
            self._button(slot, 230 + i * 75, i, "저장 데이터 없음")
        self._button("뒤로", 465, 3)
        self._text("저장 기능은 게임 내 저장 연동 후 사용할 수 있어", (500, 525), self.small, YELLOW)

    def _draw_credits(self):  # 프로젝트 크레딧 화면을 그리기
        self._text("크레딧", (500, 130), self.title_font, WHITE)
        self._text("SOLO SAT · 나 혼자만 1등급", (500, 220), self.font, YELLOW)
        self._text("2026 VIAUS 프로젝트", (500, 265), self.subtitle_font, WHITE)
        self._text("Pygame 기반 학습형 플랫폼 게임 프로토타입", (500, 305), self.small, (211, 220, 230))
        self._text("기획 · 개발: SOLO SAT 프로젝트", (500, 340), self.small, (211, 220, 230))
        self.buttons = []  # 크레딧 페이지 버튼 목록을 새로 구성
        self._button("뒤로", 425, 0)

    def draw(self):  # 현재 페이지와 유효한 알림을 그리기
        self._background()
        if self.page == "main":  # 메인 메뉴 페이지를 표시
            self._draw_main()
        elif self.page == "load":  # 저장 슬롯 페이지를 표시
            self._draw_load()
        else:
            self._draw_credits()
        if self.notice and pygame.time.get_ticks() < self.notice_until:  # 표시 시간이 남은 알림을 그리기
            self._text(self.notice, (500, 480), self.small, YELLOW)

    def _activate(self, index):  # 선택한 메뉴 항목의 동작을 수행
        if self.page == "main":  # 메인 메뉴 항목을 처리
            if index == 0:  # 새 게임 시작을 요청
                return "new_game"
            if index == 1:  # 저장 슬롯 화면으로 이동
                self.page, self.selected = "load", 0  # 저장 슬롯 페이지와 첫 선택 항목으로 이동
            elif index == 2:  # 크레딧 화면으로 이동
                return "leaderboard"
            elif index == 3:  # 게임 종료를 요청
                return "quit"
        elif self.page == "load":  # 저장 슬롯 화면 선택을 처리
            if index == 3:  # 뒤로 버튼으로 메인 메뉴에 복귀
                self.page, self.selected = "main", 0  # 메인 페이지와 첫 선택 항목으로 복귀
            else:  # 아직 저장 연동이 없는 슬롯 안내를 표시
                return "load_game"
        else:
            self.page, self.selected = "main", 0  # 하위 페이지에서 메인 메뉴로 복귀
        return None

    def run(self):  # 메뉴 입력·그리기 반복을 실행하고 선택 결과를 반환
        while self.running:
            self.clock.tick(60)
            self.draw()
            pygame.display.flip()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:  # 창 닫기 요청 시 종료를 반환
                    return "quit"
                if event.type == pygame.KEYDOWN:  # 키보드 메뉴 조작을 처리
                    if event.key == pygame.K_F11:  # F11로 전체 화면을 전환
                        self.screen = toggle_fullscreen(self.screen)  # 전체 화면으로 전환한 화면
                    elif event.key == pygame.K_ESCAPE:  # ESC 입력은 페이지를 닫거나 메인 메뉴로 복귀
                        if self.page == "main":  # 메인 페이지에서 ESC를 누르면 종료
                            return "quit"
                        self.page, self.selected = "main", 0  # 메인 페이지의 첫 항목으로 복귀
                    elif event.key in (pygame.K_UP, pygame.K_w):  # 위 항목으로 선택을 이동
                        self.selected = max(0, self.selected - 1)  # 선택 번호가 0 아래로 내려가지 않게 
                    elif event.key in (pygame.K_DOWN, pygame.K_s):  # 아래 항목으로 선택을 이동
                        max_index = 3 if self.page in ("main", "load") else 0  # 현재 페이지의 마지막 항목
                        self.selected = min(max_index, self.selected + 1)  # 페이지 마지막 항목을 넘지 않게 
                    elif event.key in (pygame.K_RETURN, pygame.K_SPACE):  # 선택된 버튼을 실행
                        result = self._activate(self.selected)  # 선택 동작의 반환값
                        if result:  # 메뉴 종료 또는 새 게임 요청을 반환
                            return result
                elif event.type == pygame.MOUSEMOTION:  # 포인터가 가리키는 버튼을 선택
                    for rect, index in self.buttons:
                        if rect.collidepoint(event.pos):  # 포인터가 버튼 위에 있는지 확인
                            self.selected = index  # 포인터가 가리키는 버튼을 선택
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  # 왼쪽 클릭한 버튼을 실행
                    for rect, index in self.buttons:
                        if rect.collidepoint(event.pos):  # 클릭 위치와 버튼 영역이 겹치는지 확인
                            result = self._activate(index)  # 클릭한 버튼의 동작 결과
                            if result:  # 메뉴 종료 또는 새 게임 요청을 반환
                                return result
        return "quit"
