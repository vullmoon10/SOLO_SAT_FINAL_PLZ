import pygame
from settings import WIDTH, HEIGHT, MAX_HP, choose_cheat
from entities.player import Player
from world.generator import World
from systems.quiz import Quiz
from systems.combat import apply_damage
from systems.progression import add_score
from ui.renderer import Renderer
from core.events import handle_quiz_event


class Game:
    def __init__(self, screen):
        self.screen = screen
        self.clock = pygame.time.Clock()
        self.cheats = choose_cheat()
        self.player = Player(cheats=self.cheats)
        self.world = World()
        self.quiz = Quiz(cheats=self.cheats)
        self.renderer = Renderer(screen)
        self.camera_x = self.score = 0
        self.hp = MAX_HP
        self.message = ""
        self.message_until = 0
        self.running = True
        self.game_over = False
        self.damage_cooldown_until = 0

    def show_message(self, text, duration=2000):
        self.message = text
        self.message_until = pygame.time.get_ticks() + duration

    def apply_quiz_result(self, result):
        if result is None:
            return
        self.score = add_score(self.score, result["score"])
        self.hp = apply_damage(self.hp, result["damage"])
        self.show_message(result["message"])
        if self.hp <= 0:
            self.game_over = True

    def open_nearby_enemy(self):
        nearby = self.player.rect.inflate(60,45)
        for enemy in self.world.enemies:
            if enemy.active and nearby.colliderect(enemy.rect):
                self.quiz.open(enemy)
                return

    def handle_event(self, event):
        if event.type == pygame.QUIT:
            self.running = False
            return
        if self.game_over:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.running = False
            return
        if self.quiz.active:
            handle_quiz_event(event,self.quiz,self.apply_quiz_result)
            return
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.running = False
            elif event.key == pygame.K_SPACE:
                self.player.jump()
            elif event.key == pygame.K_e:
                self.open_nearby_enemy()

    def update(self):
        if self.game_over or self.quiz.active:
            return
        self.player.update(pygame.key.get_pressed(),self.world)
        now = pygame.time.get_ticks()
        if now >= self.damage_cooldown_until:
            for spike in self.world.spikes:
                spike_rect = pygame.Rect(spike["x"], spike["y"] - 14, spike["count"] * 13, 14)
                if self.player.rect.colliderect(spike_rect):
                    if not self.cheats.get("no_damage"):
                        self.hp = max(0, self.hp - 10)
                    self.damage_cooldown_until = now + 900
                    self.player.rect.bottom = min(self.player.rect.bottom, 500)
                    self.player.vy = -4
                    break
        target_x = max(0,self.player.rect.x-int(WIDTH*.55))
        self.camera_x = max(self.camera_x,target_x)
        self.world.update_generation(self.player.rect.x)
        for enemy in self.world.enemies:
            if enemy.active and self.player.rect.colliderect(enemy.rect):
                self.quiz.open(enemy)
                break
        if self.player.rect.top > HEIGHT:
            self.player.reset_position()
            self.camera_x = 0
            if not self.cheats.get("no_damage"):
                self.hp = max(0, self.hp - 10)
        if self.hp <= 0:
            self.game_over = True

    def update_quiz(self):
        self.apply_quiz_result(self.quiz.check_timeout())

    def draw(self):
        self.renderer.draw_background(self.camera_x)
        self.renderer.draw_world(self.world,self.camera_x)
        self.renderer.draw_player(self.player,self.camera_x)
        message = self.message if pygame.time.get_ticks() < self.message_until else ""
        self.renderer.draw_hud(self.hp,self.score,message)
        self.renderer.draw_quiz(self.quiz)
        if self.game_over:
            overlay = pygame.Surface((WIDTH,HEIGHT),pygame.SRCALPHA)
            overlay.fill((0,0,0,190))
            self.screen.blit(overlay,(0,0))
            self.renderer.draw_text("GAME OVER",390,240,(255,255,255))
            self.renderer.draw_text(f"최종 점수: {self.score}",390,290,(255,255,255))
            self.renderer.draw_text("ESC를 눌러 종료",390,340,(255,255,255))

    def run(self):
        while self.running:
            self.clock.tick(60)
            for event in pygame.event.get():
                self.handle_event(event)
            self.update()
            self.update_quiz()
            self.draw()
            pygame.display.flip()
