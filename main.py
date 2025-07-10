
import os
import requests
from bs4 import BeautifulSoup
from win11toast import toast
import sys

url='https://computer.knu.ac.kr/bbs/board.php?bo_table=sub5_1&sca=%EC%8B%AC%EC%BB%B4'


try:
    #웹사이트 get
    data = requests.get(url)
    soup = BeautifulSoup(data.text, 'html.parser')

    #마지막 업데이트 공지 번호 읽어오기
    with open("current_list_num.txt", "r",encoding="utf-8") as f:
        current_num=f.read()

    current_num.strip()
    start_num=0
    #최근 공지 번호 get
    tbody = soup.select_one('#fboardlist > div.basic_tbl_head.tbl_wrap > table > tbody')
    for row in tbody.find_all('tr'):
        if row.get('class') != ['bo_notice']:
            new_list_num=str(row.find("td").text).strip()
            break
        else:
            start_num+=1
    
    print("startnum:" ,start_num)
    last_num=start_num+int(new_list_num)-int(current_num)
    print("lastnum: ",last_num)
    #업데이트된 공지 가져오기
    content= soup.select('div.bo_tit a')[start_num:last_num]

    #제목, 링크 분류
    title=[]
    links=[]
    for a in content:
        if(a.text):
            title.append(str(a.text).strip())
        if a.get("href"):
            links.append(str(a.attrs['href']))

    icon_path = "./knu-emblem.ico"
    icon_path = os.path.abspath(icon_path)


    while title and links:  
        toast(title.pop(),"공지 바로가기기",on_click=links.pop(),icon=icon_path)


    #최신 공지 번호 갱신
    with open("current_list_num.txt", "w", encoding="utf-8") as file:
        file.write(new_list_num)
except requests.exceptions.ConnectionError as errc:
    sys.exit(1)

