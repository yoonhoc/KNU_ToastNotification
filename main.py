import os
import sys
import requests
from bs4 import BeautifulSoup
from win11toast import toast

def main():
    url = 'https://cse.knu.ac.kr/bbs/board.php?bo_table=sub5_1&lang=kor'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    
    # Read the last checked notice number
    try:
        with open("current_list_num.txt", "r", encoding="utf-8") as f:
            current_num = int(f.read().strip())
    except (FileNotFoundError, ValueError):
        current_num = 0

    # Fetch the webpage
    try:
        res = requests.get(url, headers=headers, timeout=10)
        res.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Network error: {e}")
        sys.exit(1)

    soup = BeautifulSoup(res.text, 'html.parser')
    tbody = soup.select_one('#fboardlist > div.basic_tbl_head.tbl_wrap > table > tbody')
    
    if not tbody:
        print("Failed to find the notice table in HTML.")
        sys.exit(1)

    new_notices = []
    max_num = current_num

    # Iterate through each row in the notice table
    for row in tbody.find_all('tr'):
        # Skip pinned (important) notices
        if 'bo_notice' in row.get('class', []):
            continue
            
        num_td = row.find('td', class_='td_num2')
        if not num_td:
            continue
            
        try:
            notice_num = int(num_td.text.strip())
        except ValueError:
            continue
            
        # Keep track of the highest notice number seen
        if notice_num > max_num:
            max_num = notice_num

        # Stop searching if we reach already seen notices
        if notice_num <= current_num:
            break
            
        title_tag = row.select_one('.bo_tit a')
        if title_tag:
            title = title_tag.text.strip()
            link = title_tag.get('href', '')
            if title and link:
                new_notices.append({'title': title, 'link': link})

    icon_path = os.path.abspath("./knu-emblem.ico")
    
    # Show oldest new notices first
    for notice in reversed(new_notices):
        toast(notice['title'], "공지 바로가기", on_click=notice['link'], icon=icon_path)

    # Update the last checked notice number file if there are new notices
    if max_num > current_num:
        with open("current_list_num.txt", "w", encoding="utf-8") as f:
            f.write(str(max_num))
            print(f"Updated current_list_num.txt to {max_num}")
    else:
        print("No new notices found.")

if __name__ == "__main__":
    main()
