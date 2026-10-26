@echo off
chcp 65001 >nul
setlocal EnableDelayedExpansion

:: 0. 현재 배치 파일이 위치한 폴더(프로젝트 루트)로 작업 경로 이동 (절대 경로 하드코딩 방지)
cd /d "%~dp0"

set "ENV_NAME=SOLO_SAT"
set "PYTHON_VER=3.11"
set "ENTRY_POINT=main.py"
set "EXE_NAME=SOLO_SAT"

echo ========================================================
echo          [SOLO SAT] 환경 구성 및 자동 빌드 도구
echo ========================================================
echo 작업 경로: %CD%
echo.

:: 1. Conda 설치 여부 확인
echo [1/8] Conda 설치 여부를 확인합니다...
where conda >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo [오류] 시스템 경로(PATH)에서 Conda를 찾을 수 없습니다.
    echo.
    echo [Conda 설치 및 설정 안내]
    echo 1. Miniconda 또는 Anaconda 공식 홈페이지에서 설치 파일을 다운로드하세요.
    echo    - https://docs.conda.io/en/latest/miniconda.html
    echo 2. 설치 시 'Add Conda to my PATH environment variable' 옵션을 체크하거나,
    echo    설치 후 'Anaconda Prompt'를 실행하여 이 배치 파일을 실행해 주세요.
    goto :ERROR_EXIT
)
echo -^> Conda 확인 완료.
echo.

:: 2. SOLO_SAT Conda 환경 확인 및 생성 (Python 3.11 기반)
echo [2/8] '%ENV_NAME%' Conda 환경을 확인합니다...
call conda env list | findstr /R /C:"^%ENV_NAME%[ ]" >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo -^> '%ENV_NAME%' 환경이 존재하지 않습니다. Python %PYTHON_VER% 기반으로 새로 생성합니다...
    call conda create -n %ENV_NAME% python=%PYTHON_VER% -y
    if !ERRORLEVEL! neq 0 (
        echo [오류] Conda 가상환경 생성에 실패했습니다.
        goto :ERROR_EXIT
    )
    echo -^> 가상환경 생성 완료.
) else (
    echo -^> '%ENV_NAME%' 환경이 이미 준비되어 있습니다. (생성 생략)
)
echo.

:: 3. requirements.txt 라이브러리 확인 및 설치
echo [3/8] 필수 라이브러리(requirements.txt)를 확인하고 설치합니다...
if not exist "requirements.txt" (
    echo [오류] 프로젝트 폴더에 requirements.txt 파일이 없습니다.
    goto :ERROR_EXIT
)
:: 이미 설치된 패키지는 건너뛰어 불필요한 작업 최소화
call conda run -n %ENV_NAME% python -m pip install -r requirements.txt --quiet --disable-pip-version-check
if %ERRORLEVEL% neq 0 (
    echo [오류] requirements.txt 라이브러리 설치 중 문제가 발생했습니다.
    goto :ERROR_EXIT
)
echo -^> 라이브러리 준비 완료.
echo.

:: 4. 필요한 라이브러리가 정상적으로 import되는지 검사
echo [4/8] 주요 라이브러리 및 프로젝트 모듈 import 검사를 수행합니다...
call conda run -n %ENV_NAME% python -c "import sys, os, json, pygame; import settings; print('      -> Python:', sys.version.split()[0], '| Pygame:', pygame.__version__)"
if %ERRORLEVEL% neq 0 (
    echo [오류] 필수 라이브러리(pygame 등) 또는 기본 모듈을 불러오지 못했습니다.
    goto :ERROR_EXIT
)
echo -^> 모듈 Import 테스트 통과.
echo.

:: 5. PyInstaller 설치 및 준비
echo [5/8] PyInstaller 설치 여부를 확인합니다...
call conda run -n %ENV_NAME% python -c "import PyInstaller" >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo -^> PyInstaller가 설치되어 있지 않습니다. 설치를 진행합니다...
    call conda run -n %ENV_NAME% python -m pip install pyinstaller --quiet --disable-pip-version-check
    if !ERRORLEVEL! neq 0 (
        echo [오류] PyInstaller 설치에 실패했습니다.
        goto :ERROR_EXIT
    )
    echo -^> PyInstaller 설치 완료.
) else (
    echo -^> PyInstaller가 이미 준비되어 있습니다. (설치 생략)
)
echo.

:: 6. 프로젝트 구조와 리소스 경로 확인
echo [6/8] 프로젝트 진입점 및 필수 리소스 경로를 확인합니다...
set "MISSING_FILE=0"

if not exist "%ENTRY_POINT%" (
    echo [오류] 진입점 파일(%ENTRY_POINT%)을 찾을 수 없습니다. (주의: settings.py는 진입점이 아닙니다)
    set "MISSING_FILE=1"
)
if not exist "settings.py" (
    echo [오류] 설정 파일(settings.py)을 찾을 수 없습니다.
    set "MISSING_FILE=1"
)
if not exist "data\questions.json" (
    echo [오류] 필수 데이터 파일(data\questions.json)을 찾을 수 없습니다.
    set "MISSING_FILE=1"
)
if not exist "assets" (
    echo [오류] 리소스 폴더(assets)를 찾을 수 없습니다.
    set "MISSING_FILE=1"
)

if "%MISSING_FILE%"=="1" (
    echo [오류] 필수 파일 또는 폴더가 누락되어 빌드를 중단합니다.
    goto :ERROR_EXIT
)
echo -^> 진입점(%ENTRY_POINT%), data\questions.json, assets\ 폴더 확인 완료.
echo.

:: 7. main.py를 진입점으로 사용해 EXE 빌드
echo [7/8] PyInstaller를 사용하여 EXE 빌드를 시작합니다...
echo       (기존 빌드 캐시를 정리하고 리소스를 패키징합니다)

:: --noconfirm: 기존 dist 폴더 덮어쓰기 확인 생략
:: --onedir: 폴더 형태로 빌드하여 data/ 및 assets/ 상대 경로 구조 완벽 유지
:: --add-data: data 폴더와 assets 폴더를 EXE 결과물 내부에 복사
call conda run -n %ENV_NAME% pyinstaller --noconfirm --clean --onedir --windowed ^
    --name "%EXE_NAME%" ^
    --add-data "data;data" ^
    --add-data "assets;assets" ^
    -- copy-metadata pygame ^
    "%ENTRY_POINT%"

if %ERRORLEVEL% neq 0 (
    echo [오류] PyInstaller를 통한 EXE 빌드 중 오류가 발생했습니다.
    goto :ERROR_EXIT
)

:: PyInstaller 버전에 따라 _internal 폴더에만 리소스가 들어가는 경우를 대비해 루트에도 복사 보장
if not exist "dist\%EXE_NAME%\data\questions.json" (
    xcopy /E /I /Y "data" "dist\%EXE_NAME%\data" >nul
)
if not exist "dist\%EXE_NAME%\assets" (
    xcopy /E /I /Y "assets" "dist\%EXE_NAME%\assets" >nul
)
echo -^> EXE 빌드 및 리소스 배치 완료.
echo.

:: 8. 성공 여부와 결과물 경로 출력
echo [8/8] 모든 작업이 완료되었습니다!
echo ========================================================
echo  [빌드 결과 안내]
echo  - 상태: 빌드 스크립트 작성 완료 (실제 실행 및 빌드 테스트 미검증)
echo  - 실행 파일 위치: %CD%\dist\%EXE_NAME%\%EXE_NAME%.exe
echo  - 포함 리소스:
echo    * %CD%\dist\%EXE_NAME%\data\questions.json
echo    * %CD%\dist\%EXE_NAME%\assets\
echo ========================================================
echo.
pause
exit /b 0

:ERROR_EXIT
echo.
echo ========================================================
echo  [실패] 작업 도중 오류가 발생하여 프로세스가 중단되었습니다.
echo  위의 오류 메시지를 확인해 주세요.
echo ========================================================
echo.
pause
exit /b 1