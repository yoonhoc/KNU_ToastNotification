import requests
from bs4 import BeautifulSoup

#웹사이트 get
data = requests.get('https://computer.knu.ac.kr/bbs/board.php?bo_table=sub5_1&sca=%EC%8B%AC%EC%BB%B4')
soup = BeautifulSoup(data.text, 'html.parser')

#마지막 업데이트 공지 번호 읽어오기
with open("current_list_num.txt", "r",encoding="utf-8") as f:
    current_num=f.read()

current_num.strip()

#최근 공지 번호 get
tbody = soup.select_one('#fboardlist > div.basic_tbl_head.tbl_wrap > table > tbody')
for row in tbody.find_all('tr'):
    if row.get('class') != ['bo_notice']:
        new_list_num=str(row.find("td").text).strip()
        break

#업데이트된 공지 가져오기
content= soup.select('div.bo_tit a')[:int(new_list_num)-int(current_num)]

#제목, 링크 분류
title=[]
links=[]
for a in content:
    if(a.text):
        title.append([str(a.text).strip()])
    if a.get("href"):
        links.append(str(a.attrs['href']))

#최신 공지 번호 갱신
with open("current_list_num.txt", "w", encoding="utf-8") as file:
    file.write(new_list_num)
