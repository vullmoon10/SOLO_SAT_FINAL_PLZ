import pygame


def handle_quiz_event(event, quiz, apply_result):  # 퀴즈 입력을 처리하고 결과를 반영
    if event.type == pygame.KEYDOWN:  # 키보드 입력일 때 선택과 제출을 처리
        if event.key == pygame.K_ESCAPE:  # ESC 키로 퀴즈를 닫기
            quiz.enemy = None  # 현재 퀴즈 대상을 해제
        elif event.key in (pygame.K_UP, pygame.K_w):  # 위쪽 선택지 선택
            quiz.selected = (quiz.selected - 1) % 4  # 이전 답변으로 선택을 이동
        elif event.key in (pygame.K_DOWN, pygame.K_s):  # 아래쪽 선택지 선택
            quiz.selected = (quiz.selected + 1) % 4  # 다음 답변으로 선택을 이동
        elif event.key in (pygame.K_RETURN, pygame.K_SPACE):  # 현재 선택지를 제출
            apply_result(quiz.submit(quiz.selected))
        elif event.key in (pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4):  # 숫자 키에 해당하는 답을 제출
            apply_result(quiz.submit(event.key - pygame.K_1))
    elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  # 마우스 왼쪽 클릭으로 선택지를 제출
        for i in range(4):
            if pygame.Rect(205, 245 + i * 48, 590, 39).collidepoint(event.pos):  # 클릭 위치에 맞는 선택지를 찾기
                apply_result(quiz.submit(i))
                break
