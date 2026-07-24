# KNU Toast Notification

경북대학교 컴퓨터학부 홈페이지의 새 공지사항을 확인하여 Windows 알림으로
표시하는 프로그램입니다. 알림을 클릭하면 해당 공지 페이지가 열립니다.

## 주요 동작

- 일반 공지 중 마지막 확인 번호보다 새 번호인 게시글만 알립니다.
- 새 공지는 오래된 순서부터 표시합니다.
- 상태와 로그는 작업 폴더가 아닌 사용자별 로컬 앱 데이터에 저장합니다.
- 네트워크, HTML 파싱, 알림 오류는 회전 로그에 기록합니다.
- 실행 파일에는 경북대학교 엠블럼이 포함됩니다.

사용자 데이터 경로:

```text
%LOCALAPPDATA%\KNUToastNotification\
├── current_list_num.txt
└── knu-toast.log
```

## 소스 실행

Python 3이 필요합니다.

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe main.py --dry-run
.\.venv\Scripts\python.exe main.py
```

옵션:

- `--initialize`: 현재 최신 번호를 기준점으로 저장하며 알림은 보내지 않습니다.
- `--dry-run`: 게시판 연결과 파싱만 검사하며 알림과 상태는 변경하지 않습니다.

## 테스트

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
.\.venv\Scripts\python.exe -m py_compile main.py
```

## Windows 실행 파일 빌드

```powershell
.\.venv\Scripts\python.exe -m pip install pyinstaller
.\.venv\Scripts\pyinstaller.exe --clean --noconfirm main.spec
```

결과물은 `dist\KNUToastNotification.exe`입니다. `dist`는 빌드 결과물이므로
Git에는 포함하지 않습니다.

## 작업 스케줄러 등록

PowerShell에서 다음 명령을 실행하면 현재 최신 공지를 기준점으로 초기화한 뒤
현재 사용자가 로그온할 때와 이후 30분마다 실행되도록 등록합니다. 배터리 사용
중에도 실행되며, 이전 실행이 끝나지 않았다면 중복 실행하지 않습니다.

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\register-task.ps1
```

실행 간격을 바꾸려면 다음과 같이 지정합니다.

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\register-task.ps1 `
  -IntervalMinutes 60
```

등록되는 작업 이름은 `KNU_ToastNotification`입니다. 같은 이름의 기존 작업은
새 설정으로 교체됩니다.
