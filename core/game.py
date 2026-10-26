import pygame
from settings import WIDTH, HEIGHT, MAX_HP, choose_cheat
from entities.player import Player
from world.generator import World
from systems.quiz import Quiz
from systems.combat import apply_damage
from systems.progression import add_score
from ui.renderer import Renderer
from core.events import handle_quiz_event
from core.display import toggle_fullscreen


class Game:  # 플레이어·월드·퀴즈를 묶어 게임 진행을 관리한다.
    def __init__(self, screen):  # 화면과 게임 시스템의 초기 상태를 설정한다.
        self.screen = screen  # 현재 게임 화면
        self.clock = pygame.time.Clock()  # 프레임 속도 조절 시계
        self.cheats = choose_cheat()  # 실행 환경에서 선택한 치트 설정
        self.player = Player(cheats=self.cheats)  # 플레이어 객체
        self.world = World()  # 진행 중 생성되는 게임 월드
        self.quiz = Quiz(cheats=self.cheats)  # 적과 연결된 퀴즈 시스템
        self.renderer = Renderer(screen)  # 화면 렌더러
        self.camera_x = self.score = 0  # 카메라 시작 좌표와 초기 점수
        self.hp = MAX_HP  # 플레이어의 시작 체력
        self.message = ""  # 화면에 표시할 알림 문구
        self.message_until = 0  # 알림 표시 종료 시각
        self.running = True  # 메인 루프 실행 여부
        self.game_over = False  # 게임 오버 상태
        self.damage_cooldown_until = 0  # 다음 충돌 피해가 허용되는 시각

    def show_message(self, text, duration=2000):  # 일정 시간 동안 화면 알림을 표시한다.
        self.message = text  # 표시할 알림 내용
        self.message_until = pygame.time.get_ticks() + duration  # 알림 종료 시각

    def apply_quiz_result(self, result):  # 퀴즈 결과에 따라 점수와 체력을 갱신한다.
        if result is None:  # 결과가 없으면 반영할 작업이 없다.
            return
        self.score = add_score(self.score, result["score"])  # 퀴즈에서 획득한 점수를 누적한다.
        self.hp = apply_damage(self.hp, result["damage"])  # 퀴즈 결과 피해량을 체력에 반영한다.
        self.show_message(result["message"])
        if self.hp <= 0:  # 체력이 모두 소진되면 게임 오버로 전환한다.
            self.game_over = True  # 체력이 다하면 게임 오버 상태로 바꾼다.

    def open_nearby_enemy(self):  # 플레이어 주변에 있는 적의 퀴즈를 연다.
        nearby = self.player.rect.inflate(60,45)  # 상호작용을 위한 탐색 범위
        for enemy in self.world.enemies:
            if enemy.active and nearby.colliderect(enemy.rect):  # 활성 상태이며 범위 안인 적을 찾는다.
                self.quiz.open(enemy)
                return

    def handle_event(self, event):  # 현재 상태에 맞춰 게임 입력을 처리한다.
        if event.type == pygame.QUIT:  # 창 닫기 요청 시 게임 루프를 끝낸다.
            self.running = False  # 게임 반복을 종료하도록 설정한다.
            return
        if event.type == pygame.KEYDOWN and event.key == pygame.K_F11:  # F11로 전체 화면을 전환한다.
            self.screen = toggle_fullscreen(self.screen)  # 전체 화면으로 전환한 화면
            self.renderer.screen = self.screen  # 렌더러의 화면 참조도 갱신한다.
            return
        if self.game_over:  # 게임 오버 중에는 종료 입력만 받는다.
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:  # ESC로 게임을 종료한다.
                self.running = False  # 게임 반복을 종료하도록 설정한다.
            return
        if self.quiz.active:  # 퀴즈가 열려 있으면 입력을 퀴즈 처리기로 전달한다.
            handle_quiz_event(event,self.quiz,self.apply_quiz_result)
            return
        if event.type == pygame.KEYDOWN:  # 일반 게임 중 키보드 조작을 처리한다.
            if event.key == pygame.K_ESCAPE:  # ESC로 게임을 종료한다.
                self.running = False  # 게임 반복을 종료하도록 설정한다.
            elif event.key == pygame.K_SPACE:  # 스페이스 키로 점프한다.
                self.player.jump()
            elif event.key == pygame.K_e:  # E 키로 주변 적의 퀴즈를 연다.
                self.open_nearby_enemy()

    def update(self):  # 플레이어·충돌·카메라·월드 상태를 갱신한다.
        if self.game_over or self.quiz.active:  # 게임 오버 또는 퀴즈 중에는 월드를 멈춘다.
            return
        self.player.update(pygame.key.get_pressed(),self.world)
        now = pygame.time.get_ticks()  # 현재 게임 경과 시각
        if now >= self.damage_cooldown_until:  # 피해 재적용 대기 시간이 끝났는지 확인한다.
            for spike in self.world.spikes:
                spike_rect = pygame.Rect(spike["x"], spike["y"] - 14, spike["count"] * 13, 14)  # 가시 충돌 영역
                if self.player.rect.colliderect(spike_rect):  # 플레이어가 가시에 닿았는지 확인한다.
                    if not self.cheats.get("no_damage"):  # 무피해 치트가 없으면 체력을 감소시킨다.
                        self.hp = max(0, self.hp - 10)  # 가시 피해를 적용한 체력
                    self.damage_cooldown_until = now + 900  # 다음 피해 판정 가능 시각
                    self.player.rect.bottom = min(self.player.rect.bottom, 500)  # 가시에서 플레이어를 밀어낸다.
                    self.player.vy = -4  # 가시 충돌 후 위쪽 반동 속도
                    break
        target_x = max(0,self.player.rect.x-int(WIDTH*.55))  # 플레이어를 화면 기준 위치에 두는 카메라 좌표
        self.camera_x = max(self.camera_x,target_x)  # 카메라가 뒤로 움직이지 않도록 위치를 갱신한다.
        self.world.update_generation(self.player.rect.x)
        for enemy in self.world.enemies:
            if enemy.active and self.player.rect.colliderect(enemy.rect):  # 살아 있는 적과 접촉하면 퀴즈를 연다.
                self.quiz.open(enemy)
                break
        if self.player.rect.top > HEIGHT:  # 화면 아래로 떨어지면 시작 위치로 되돌린다.
            self.player.reset_position()
            self.camera_x = 0  # 시작 위치에 맞춰 카메라를 초기화한다.
            if not self.cheats.get("no_damage"):  # 무피해 치트가 없으면 추락 피해를 적용한다.
                self.hp = max(0, self.hp - 10)  # 추락 피해를 반영한 체력
        if self.hp <= 0:  # 체력이 모두 소진되면 게임 오버로 전환한다.
            self.game_over = True  # 체력이 다하면 게임 오버 상태로 바꾼다.

    def update_quiz(self):  # 퀴즈 시간 초과 결과를 게임에 반영한다.
        self.apply_quiz_result(self.quiz.check_timeout())

    def draw(self):  # 게임 화면과 현재 상태 UI를 그린다.
        self.renderer.draw_background(self.camera_x)
        self.renderer.draw_world(self.world,self.camera_x)
        self.renderer.draw_player(self.player,self.camera_x)
        message = self.message if pygame.time.get_ticks() < self.message_until else ""  # 표시 시간이 남은 알림만 전달한다.
        self.renderer.draw_hud(self.hp,self.score,message)
        self.renderer.draw_quiz(self.quiz)
        if self.game_over:  # 게임 오버 화면을 추가로 표시한다.
            overlay = pygame.Surface((WIDTH,HEIGHT),pygame.SRCALPHA)  # 화면을 어둡게 덮는 투명 레이어
            overlay.fill((0,0,0,190))
            self.screen.blit(overlay,(0,0))
            self.renderer.draw_text("GAME OVER",390,240,(255,255,255))
            self.renderer.draw_text(f"최종 점수: {self.score}",390,290,(255,255,255))
            self.renderer.draw_text("ESC를 눌러 종료",390,340,(255,255,255))

    def run(self):  # 게임 루프를 실행하고 매 프레임 상태를 갱신한다.
        while self.running:
            self.clock.tick(60)
            for event in pygame.event.get():
                self.handle_event(event)
            self.update()
            self.update_quiz()
            self.draw()
            pygame.display.flip()
