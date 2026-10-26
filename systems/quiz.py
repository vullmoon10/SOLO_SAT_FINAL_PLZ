import json
import random
from pathlib import Path
import pygame
from settings import WRONG_DAMAGE, QUESTION_TIME

_DATA_PATH = Path(__file__).resolve().parents[1] / "data" / "questions.json"  # 문제 데이터 파일 경로
try:
    QUESTIONS = json.loads(_DATA_PATH.read_text(encoding="utf-8"))  # JSON에서 문제 목록을 불러오기
except (OSError, json.JSONDecodeError):
    QUESTIONS = []  # 파일 오류 시 비어 있는 문제 목록으로 초기화


def get_random_question(difficulty=None):  # 지정 난이도에 맞는 무작위 문제를 반환
    pool = [q for q in QUESTIONS if difficulty is None or q.get("difficulty") == difficulty]  # 난이도에 맞는 문제 후보
    if not pool:  # 해당 난이도 문제가 없으면 전체 문제를 후보로 사용
        pool = QUESTIONS  # 난이도 제한 없이 전체 문제를 후보로 사용
    if not pool:  # 데이터가 비어 있으면 기본 문제를 반환
        return {"subject": "수학", "difficulty": "easy", "q": "3 + 8 = ?", "choices": ["21", "12", "10", "11"], "answer": 3, "time": 30}
    return random.choice(pool)


class Quiz:  # 적과 연결된 문제·선택·시간 제한 상태를 관리
    def __init__(self, cheats=None):  # 퀴즈 제한 시간과 초기 상태를 준비
        self.enemy = None  # 현재 퀴즈 대상 적
        self.started = 0  # 문제 시작 시각
        self.duration = QUESTION_TIME  # 문제 제한 시간
        self.selected = 0  # 현재 선택한 답 번호
        self.feedback = ""  # 정답·오답 피드백 문구
        self.feedback_until = 0  # 피드백 표시 종료 시각
        self.cheats = cheats or {}  # 퀴즈에 적용할 치트 설정

    @property
    def active(self):  # 퀴즈가 열려 있는지 반환
        return self.enemy is not None

    def open(self, enemy):  # 활성 적의 문제를 열고 제한 시간을 시작
        if enemy.active:  # 처치되지 않은 적만 대상으로 설정
            self.enemy = enemy  # 퀴즈 대상 적을 설정
            self.started = pygame.time.get_ticks()  # 문제 시작 시각을 기록
            self.duration = enemy.question.get("time", QUESTION_TIME)  # 문제별 제한 시간을 적용
            self.selected = 0  # 첫 번째 선택지를 기본 선택

    def remaining(self):  # 제한 시간에서 경과 시간을 빼 남은 초를 반환
        return max(0, self.duration - (pygame.time.get_ticks() - self.started) / 1000)

    def submit(self, index):  # 답을 채점하고 점수·피해 결과를 반환
        if not self.active:  # 열린 문제가 없으면 제출 결과가 없음
            return None
        question = self.enemy.question  # 현재 적이 출제한 문제
        if not 0 <= index < len(question["choices"]):  # 선택 번호가 유효 범위를 벗어나면 무시
            return None
        enemy = self.enemy  # 답변 처리 중 사용할 현재 적
        if index == question["answer"]:  # 정답이면 점수를 주고 적 체력을 감소
            score = enemy.data["score"]  # 적 처치 시 획득 점수
            result = {"correct": True, "damage": 0, "score": score, "defeated": enemy.defeat(), "message": f"정답! +{score}점"}  # 정답 처리 결과
        else:
            damage = 0 if self.cheats.get("no_damage") else WRONG_DAMAGE  # 오답 피해량(무피해 치트 적용)
            result = {"correct": False, "damage": damage, "score": 0, "defeated": False, "message": "오답! 피해 없음" if damage == 0 else f"오답! 체력 -{damage}"}  # 오답 처리 결과
        self.feedback = result["message"]  # 결과 피드백 문구
        self.feedback_until = pygame.time.get_ticks() + 1000  # 피드백 표시 종료 시각
        self.enemy = None  # 답변 처리 후 퀴즈를 닫기
        return result

    def check_timeout(self):  # 제한 시간 초과 여부를 확인해 피해 결과를 반환
        if self.active and self.remaining() <= 0:  # 문제가 열린 채 시간이 끝났는지 확인
            damage = 0 if self.cheats.get("no_damage") else WRONG_DAMAGE  # 시간 초과 피해량(무피해 치트 적용)
            self.feedback = "시간 초과!"  # 제한 시간 초과 안내
            self.feedback_until = pygame.time.get_ticks() + 1000  # 피드백 표시 종료 시각
            self.enemy = None  # 시간 초과 후 퀴즈를 닫기
            return {"correct": False, "damage": damage, "score": 0, "defeated": False, "message": "시간 초과!"}
        return None
