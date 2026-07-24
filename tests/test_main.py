import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import main


SAMPLE_HTML = """
<div id="fboardlist">
  <table>
    <tbody>
      <tr class="bo_notice">
        <td class="td_num2">공지</td>
        <td class="bo_tit"><a href="/pinned">고정 공지</a></td>
      </tr>
      <tr>
        <td class="td_num2">102</td>
        <td class="bo_tit"><a href="/notice/102"> 새 공지 102 </a></td>
      </tr>
      <tr>
        <td class="td_num2">101</td>
        <td class="bo_tit"><a href="https://example.com/notice/101">새 공지 101</a></td>
      </tr>
      <tr>
        <td class="td_num2">100</td>
        <td class="bo_tit"><a href="/notice/100">기존 공지</a></td>
      </tr>
    </tbody>
  </table>
</div>
"""


class ParseNoticesTests(unittest.TestCase):
    def test_returns_only_new_notices_in_oldest_first_order(self):
        notices, latest = main.parse_notices(
            SAMPLE_HTML,
            current_number=100,
            base_url="https://example.com/board",
        )

        self.assertEqual([notice.number for notice in notices], [101, 102])
        self.assertEqual(notices[1].title, "새 공지 102")
        self.assertEqual(notices[1].link, "https://example.com/notice/102")
        self.assertEqual(latest, 102)

    def test_raises_when_notice_table_is_missing(self):
        with self.assertRaisesRegex(ValueError, "공지사항 테이블"):
            main.parse_notices("<html></html>", current_number=0)


class StateTests(unittest.TestCase):
    def test_state_round_trip(self):
        with tempfile.TemporaryDirectory() as temporary_dir:
            state_path = Path(temporary_dir) / "state" / "current.txt"

            self.assertEqual(main.read_state(state_path), 0)
            main.write_state(state_path, 123)
            self.assertEqual(main.read_state(state_path), 123)

    def test_app_data_dir_uses_local_app_data(self):
        with patch.dict(os.environ, {"LOCALAPPDATA": r"C:\LocalData"}):
            self.assertEqual(
                main.app_data_dir(),
                Path(r"C:\LocalData") / main.APP_NAME,
            )


if __name__ == "__main__":
    unittest.main()
