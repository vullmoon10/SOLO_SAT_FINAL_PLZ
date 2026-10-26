# SOLO SAT — Pygame 통합 프로토타입

## 실행
1. Python 3.10 이상 권장
2. 터미널에서 `python -m pip install -r requirements.txt`
3. `python main.py`

Windows에서는 `run_game.py.bat`을 실행해도 된다.

## 조작
- A/D 또는 ←/→: 이동
- Space: 점프
- W/S 또는 ↑/↓: 사다리 오르내리기
- E: 근처 몬스터와 상호작용
- 문제 창: ↑/↓ 선택, Enter 제출, 1~4 즉시 선택, 마우스 클릭
- F11: 전체화면 전환 (메뉴 및 게임 중)
- ESC: 게임에서 메인 메뉴로 돌아가기 (문제 창이 열려 있을 때는 기존 동작 유지)
- 메인 메뉴: 새 게임, 불러오기, 크레딧, 종료 / 키보드 및 마우스 조작

## 구성
- `core/`: 게임 루프와 이벤트 처리
- `entities/`: 플레이어와 몬스터
- `world/`: 지형·발판·사다리·장애물 생성
- `systems/`: 문제·전투·성장·저장 관련 로직
- `ui/`: 렌더링과 HUD
- `data/questions.json`: 문제 데이터

## 치트 모드(선택)
기본 실행은 일반 모드다. 치트를 쓸 경우 실행 전에 `SOLO_SAT_CHEAT` 환경변수에 1~5를 설정한다.
- 1: No Damage
- 2: Hyper Speed
- 3: Hyper Jump
- 4: Hyper Diagonal
- 5: Ultimate

PowerShell 예시: `$env:SOLO_SAT_CHEAT="1"; python main.py`

## 범위 및 주의
이 ZIP은 `code.zip`의 Pygame 구현을 기준으로, `final.zip`의 모듈 분리 방향과 저장 시스템 개념, SOLO SAT PDF의 과목·티어/랭크 기획을 참조해 통합한 실행 프로토타입이다. 기존 저장 시스템은 데이터 모델이 달라 자동 이어하기 화면까지 연결되어 있지 않으며, 티어/랭크/XP와 6개 과목별 문제 은행은 후속 구현 대상이다. PDF에 있는 전체 기획을 모두 구현했다고 간주하면 안 된다.
