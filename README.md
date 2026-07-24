# KNU Toast Notification

경북대학교 컴퓨터학부 홈페이지에 새 공지가 올라오면 Windows 알림으로
알려주는 프로그램입니다. 알림을 클릭하면 해당 공지 페이지가 바로 열립니다.

한 번 설치하면 프로그램을 직접 실행할 필요가 없습니다. Windows에 로그인할
때 한 번 확인하고, 이후 30분마다 자동으로 새 공지를 확인합니다.

## 준비물

- Windows 10 또는 Windows 11
- Python 3.10 이상
- 인터넷 연결

Python이 없다면 [Python 공식 홈페이지](https://www.python.org/downloads/windows/)에서
설치하세요. 설치 화면에서 **Add Python to PATH**를 반드시 선택해야 합니다.

## 가장 쉬운 설치 방법

### 1. 프로젝트 내려받기

GitHub 페이지 상단의 **Code → Download ZIP**을 누르고 원하는 위치에 압축을
풉니다.

Git을 사용한다면 다음 명령으로 내려받을 수도 있습니다.

```powershell
git clone https://github.com/yoonhoc/KNU_ToastNotification.git
cd KNU_ToastNotification
```

### 2. 프로젝트 폴더에서 PowerShell 열기

압축을 푼 프로젝트 폴더를 파일 탐색기로 연 뒤, 주소 표시줄에
`powershell`을 입력하고 Enter를 누릅니다.

### 3. 아래 명령을 순서대로 실행하기

아래 명령은 전용 Python 환경 생성 → 필요한 패키지 설치 → Windows 실행 파일
빌드 → 자동 실행 등록 순서로 진행됩니다.

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt pyinstaller
.\.venv\Scripts\pyinstaller.exe --clean --noconfirm main.spec
powershell -ExecutionPolicy Bypass -File .\scripts\register-task.ps1
```

다음 메시지가 표시되면 설치가 끝난 것입니다.

```text
Scheduled task registered: KNU_ToastNotification
```

설치 시점의 최신 공지 번호를 기준으로 저장하므로 기존 공지가 한꺼번에
알림으로 표시되지 않습니다. 이후에 등록되는 새 공지부터 알림이 옵니다.

## 설치 확인

PowerShell에서 다음 명령을 실행합니다.

```powershell
Get-ScheduledTask -TaskName KNU_ToastNotification
```

`State`가 `Ready` 또는 `Running`이면 정상적으로 등록된 것입니다. 즉시 한 번
실행해 보고 싶다면 다음 명령을 사용하세요.

```powershell
Start-ScheduledTask -TaskName KNU_ToastNotification
```

실행 결과는 다음 명령으로 확인할 수 있습니다. `LastTaskResult`가 `0`이면
성공입니다.

```powershell
Get-ScheduledTaskInfo -TaskName KNU_ToastNotification
```

## 자주 사용하는 설정

### 확인 주기 바꾸기

기본 확인 주기는 30분입니다. 예를 들어 60분으로 바꾸려면 등록 명령을 다시
실행합니다.

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\register-task.ps1 `
  -IntervalMinutes 60
```

설정 가능한 범위는 5분부터 1,440분까지입니다.

### 현재 공지를 새 기준점으로 설정하기

지금까지 올라온 공지는 건너뛰고 이후 공지만 받고 싶을 때 사용합니다.

```powershell
.\dist\KNUToastNotification.exe --initialize
```

### 연결 상태만 점검하기

알림을 보내거나 기준 번호를 변경하지 않고 게시판 연결과 파싱만 확인합니다.

```powershell
.\.venv\Scripts\python.exe main.py --dry-run
```

## 문제가 생겼을 때

### `python` 명령을 찾을 수 없다고 나오는 경우

Python을 다시 설치하면서 **Add Python to PATH**를 선택하거나, 설치 후
PowerShell을 완전히 닫았다가 다시 여세요.

### 알림이 오지 않는 경우

다음 순서로 확인하세요.

1. `Get-ScheduledTask -TaskName KNU_ToastNotification`으로 작업이 등록됐는지 확인합니다.
2. `Start-ScheduledTask -TaskName KNU_ToastNotification`으로 직접 실행합니다.
3. 아래 로그 파일을 열어 마지막 오류를 확인합니다.

```text
%LOCALAPPDATA%\KNUToastNotification\knu-toast.log
```

상태와 로그 파일은 다음 위치에 저장됩니다.

```text
%LOCALAPPDATA%\KNUToastNotification\
├── current_list_num.txt
└── knu-toast.log
```

### 예전 `KNU_알림` 작업이 남아 있는 경우

과거 버전을 사용했다면 관리자 권한 PowerShell에서 다음 명령으로 기존 작업을
삭제할 수 있습니다.

```powershell
schtasks /Delete /TN "\KNU_알림" /F
```

## 삭제 방법

자동 실행 작업을 제거합니다.

```powershell
Unregister-ScheduledTask -TaskName KNU_ToastNotification -Confirm:$false
```

그다음 내려받은 프로젝트 폴더를 삭제하면 됩니다. 기준 번호와 로그까지
삭제하려면 파일 탐색기 주소 표시줄에 아래 경로를 입력해 해당 폴더를
삭제하세요.

```text
%LOCALAPPDATA%\KNUToastNotification
```

## 개발자용

### 소스 직접 실행

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe main.py
```

지원 옵션:

- `--initialize`: 현재 최신 번호를 저장하고 알림은 보내지 않습니다.
- `--dry-run`: 연결과 파싱만 검사하고 알림과 상태는 변경하지 않습니다.

### 테스트

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
.\.venv\Scripts\python.exe -m py_compile main.py
```

### 실행 파일 빌드

```powershell
.\.venv\Scripts\python.exe -m pip install pyinstaller
.\.venv\Scripts\pyinstaller.exe --clean --noconfirm main.spec
```

빌드 결과물은 `dist\KNUToastNotification.exe`입니다. `dist` 폴더는 빌드
결과물이므로 Git에는 포함하지 않습니다.
