import pygame


def handle_quiz_event(event, quiz, apply_result):
    if event.type == pygame.KEYDOWN:
        if event.key == pygame.K_ESCAPE:
            quiz.enemy = None
        elif event.key in (pygame.K_UP, pygame.K_w):
            quiz.selected = (quiz.selected - 1) % 4
        elif event.key in (pygame.K_DOWN, pygame.K_s):
            quiz.selected = (quiz.selected + 1) % 4
        elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
            apply_result(quiz.submit(quiz.selected))
        elif event.key in (pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4):
            apply_result(quiz.submit(event.key - pygame.K_1))
    elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
        for i in range(4):
            if pygame.Rect(205, 245 + i * 48, 590, 39).collidepoint(event.pos):
                apply_result(quiz.submit(i))
                break
