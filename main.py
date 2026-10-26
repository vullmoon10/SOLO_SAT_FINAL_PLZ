import os
import pygame

from settings import WIDTH, HEIGHT, TITLE
from core.game import Game
from network.client import BoothClient
from systems.quiz import set_question_source
from ui.menu import Menu
from systems.subjects import SUBJECTS


def _select_subject():
    print("\n출제 과목을 선택하세요.")
    for index, subject in enumerate(SUBJECTS, 1):
        print(f"{index}. {subject}")
    while True:
        value = input("과목 번호: ").strip()
        if value.isdigit() and 1 <= int(value) <= len(SUBJECTS):
            return SUBJECTS[int(value) - 1]
        print("목록에 있는 번호를 입력하세요.")


def _new_session(client):
    nickname = input("닉네임 (비우면 player-n으로 지정): ").strip()
    subject = _select_subject()
    session = client.start_session(nickname, subject)
    questions = client.questions(subject)
    if not questions:
        print(f"{subject} 과목의 공개된 2점 문항이 없습니다. 관리자 모드에서 PDF 등록과 검수를 진행하세요.")
        return None
    set_question_source(subject, client, questions)
    return session, None


def _load_session(client):
    available = client.available_sessions()
    if not available:
        print("불러올 자동 저장 기록이 없습니다.")
        return None
    print("\n자동 저장 목록")
    for index, entry in enumerate(available, 1):
        print(f"{index}. {entry['nickname']} (기록 번호 {entry['player_id']})")
    while True:
        value = input("불러올 번호 (Enter 취소): ").strip()
        if not value:
            return None
        if value.isdigit() and 1 <= int(value) <= len(available):
            entry = available[int(value) - 1]
            state = client.load(entry["player_id"])
            if not state:
                print("저장 기록을 읽지 못했습니다.")
                return None
            subject = state.get("subject", "수학")
            questions = client.questions(subject)
            if not questions:
                print(f"{subject} 과목에 공개된 문항이 없습니다.")
                return None
            set_question_source(subject, client, questions)
            return {"player_id": entry["player_id"], "nickname": entry["nickname"], "subject": subject}, state
        print("목록 번호를 입력하세요.")


def _print_leaderboard(client):
    try:
        rows = client.leaderboard()
    except RuntimeError as exc:
        print(exc)
        return
    print("\n=== 부스 랭킹 ===")
    for rank, row in enumerate(rows, 1):
        print(f"{rank:>2}. {row['nickname']} · {row['score']}점 · {row['subject']}")


def main():
    print("SOLO SAT 부팅 메뉴")
    print("1. 사용자 모드")
    print("2. 관리자 모드 (서버 노트북에서 실행)")
    mode = input("선택: ").strip()
    if mode == "2":
        from ui.admin import run_admin
        run_admin()
        return
    if mode != "1":
        print("실행을 취소했습니다.")
        return

    client = BoothClient(os.environ.get("SOLO_SAT_SERVER"))
    try:
        client.request("GET", "/health")
    except RuntimeError as exc:
        print(exc)
        address = input("관리자 노트북 IP와 포트 입력 (예: http://192.168.0.10:8765, Enter=이 컴퓨터): ").strip()
        client = BoothClient(address or "http://127.0.0.1:8765")
        try:
            client.request("GET", "/health")
        except RuntimeError as retry_exc:
            print(retry_exc)
            return

    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption(TITLE)
    try:
        while True:
            action = Menu(screen).run()
            screen = pygame.display.get_surface()
            if action == "quit":
                break
            if action == "new_game":
                try:
                    selected = _new_session(client)
                except RuntimeError as exc:
                    print(exc)
                    continue
                if selected:
                    session, state = selected
                    Game(screen, client, session, state).run()
            elif action == "load_game":
                try:
                    selected = _load_session(client)
                except RuntimeError as exc:
                    print(exc)
                    continue
                if selected:
                    session, state = selected
                    Game(screen, client, session, state).run()
            elif action == "leaderboard":
                _print_leaderboard(client)
    finally:
        pygame.quit()


if __name__ == "__main__":
    main()
