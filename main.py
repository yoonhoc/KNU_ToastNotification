from __future__ import annotations

import argparse
import logging
import os
import sys
from dataclasses import dataclass
from logging.handlers import RotatingFileHandler
from pathlib import Path
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup
from win11toast import toast

APP_NAME = "KNUToastNotification"
NOTICE_URL = "https://cse.knu.ac.kr/bbs/board.php?bo_table=sub5_1&lang=kor"
USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
)

LOGGER = logging.getLogger(APP_NAME)


@dataclass(frozen=True)
class Notice:
    number: int
    title: str
    link: str


def app_data_dir() -> Path:
    local_app_data = os.environ.get("LOCALAPPDATA")
    base_dir = Path(local_app_data) if local_app_data else Path.home() / "AppData" / "Local"
    return base_dir / APP_NAME


def resource_path(filename: str) -> Path:
    bundle_dir = getattr(sys, "_MEIPASS", None)
    base_dir = Path(bundle_dir) if bundle_dir else Path(__file__).resolve().parent
    return base_dir / filename


def configure_logging() -> Path:
    data_dir = app_data_dir()
    data_dir.mkdir(parents=True, exist_ok=True)
    log_path = data_dir / "knu-toast.log"

    if not LOGGER.handlers:
        handler = RotatingFileHandler(
            log_path,
            maxBytes=512 * 1024,
            backupCount=3,
            encoding="utf-8",
        )
        handler.setFormatter(
            logging.Formatter("%(asctime)s %(levelname)s %(message)s")
        )
        LOGGER.addHandler(handler)
        LOGGER.setLevel(logging.INFO)

    return log_path


def read_state(state_path: Path) -> int:
    try:
        return int(state_path.read_text(encoding="utf-8").strip())
    except FileNotFoundError:
        return 0
    except (OSError, ValueError):
        LOGGER.warning("상태 파일을 읽을 수 없어 0으로 초기화합니다: %s", state_path)
        return 0


def write_state(state_path: Path, notice_number: int) -> None:
    state_path.parent.mkdir(parents=True, exist_ok=True)
    temporary_path = state_path.with_suffix(f"{state_path.suffix}.tmp")
    temporary_path.write_text(str(notice_number), encoding="utf-8")
    temporary_path.replace(state_path)


def fetch_notice_page() -> str:
    response = requests.get(
        NOTICE_URL,
        headers={"User-Agent": USER_AGENT},
        timeout=10,
    )
    response.raise_for_status()
    return response.text


def parse_notices(
    html: str,
    current_number: int,
    base_url: str = NOTICE_URL,
) -> tuple[list[Notice], int]:
    soup = BeautifulSoup(html, "html.parser")
    tbody = soup.select_one("#fboardlist table tbody")
    if tbody is None:
        raise ValueError("공지사항 테이블을 찾을 수 없습니다.")

    notices: list[Notice] = []
    latest_number = current_number

    for row in tbody.select("tr"):
        if "bo_notice" in row.get("class", []):
            continue

        number_cell = row.select_one("td.td_num2")
        title_link = row.select_one(".bo_tit a")
        if number_cell is None or title_link is None:
            continue

        try:
            notice_number = int(number_cell.get_text(strip=True))
        except ValueError:
            continue

        title = title_link.get_text(" ", strip=True)
        href = title_link.get("href")
        if not title or not href:
            continue

        latest_number = max(latest_number, notice_number)
        if notice_number > current_number:
            notices.append(
                Notice(
                    number=notice_number,
                    title=title,
                    link=urljoin(base_url, href),
                )
            )

    notices.sort(key=lambda notice: notice.number)
    return notices, latest_number


def show_notifications(notices: list[Notice]) -> None:
    icon_path = resource_path("knu-emblem.ico")
    if not icon_path.exists():
        raise FileNotFoundError(f"알림 아이콘을 찾을 수 없습니다: {icon_path}")

    for notice in notices:
        toast(
            notice.title,
            "공지 바로가기",
            on_click=notice.link,
            icon=str(icon_path),
        )


def check_notices(*, initialize: bool = False, dry_run: bool = False) -> int:
    state_path = app_data_dir() / "current_list_num.txt"
    current_number = read_state(state_path)
    notices, latest_number = parse_notices(fetch_notice_page(), current_number)

    if initialize:
        write_state(state_path, latest_number)
        LOGGER.info("기준 공지 번호를 %s로 초기화했습니다.", latest_number)
        return 0

    if dry_run:
        LOGGER.info(
            "점검 완료: 기준=%s, 최신=%s, 새 공지=%s개",
            current_number,
            latest_number,
            len(notices),
        )
        return 0

    if notices:
        show_notifications(notices)

    if latest_number > current_number:
        write_state(state_path, latest_number)

    LOGGER.info(
        "확인 완료: 기준=%s, 최신=%s, 알림=%s개",
        current_number,
        latest_number,
        len(notices),
    )
    return 0


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="경북대학교 컴퓨터학부 공지 알리미")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument(
        "--initialize",
        action="store_true",
        help="현재 최신 공지를 기준점으로 저장하고 알림은 보내지 않습니다.",
    )
    mode.add_argument(
        "--dry-run",
        action="store_true",
        help="게시판 파싱만 확인하고 알림과 상태 변경은 하지 않습니다.",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    log_path = configure_logging()
    args = parse_args(argv)

    try:
        return check_notices(initialize=args.initialize, dry_run=args.dry_run)
    except Exception:
        LOGGER.exception("공지 확인 중 오류가 발생했습니다. 로그: %s", log_path)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
