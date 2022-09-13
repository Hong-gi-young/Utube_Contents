# 크롤링 라이브러리 Import
from selenium import webdriver
import time
from bs4 import BeautifulSoup
import numpy as np
import pandas as pd
import time
import random
import warnings
import itertools
import matplotlib.pyplot as plt
from datetime import datetime,timedelta
from selenium.webdriver.common.keys import Keys
from dateutil.relativedelta import relativedelta
warnings.filterwarnings('ignore')


chrome_options = webdriver.ChromeOptions()
# chrome_options.add_argument('--headless')
chrome_options.add_argument('--no-sandbox')
chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
chrome_options.add_argument('--disable-gpu')  
# chrome_options.add_argument('--disable-dev-shm-usage')
# chrome_options.add_argument('--disable-software-rasterizer')
driver = webdriver.Chrome('chromedriver.exe', chrome_options=chrome_options)

#target of crawling
data_list = []
driver.get("https://www.youtube.com/watch?v=QndOyQtTHUQ")
time.sleep(10)
first_page = driver.execute_script("return document.documentElement.scrollHeight")

# 영상재상 중지
def play_stop(driver):
    driver.implicitly_wait(100)
    time.sleep(60)
    html = driver.page_source
    soup = BeautifulSoup(html,'html.parser')
    temp = soup.find('button',class_='ytp-play-button ytp-button')['title'].split(' ')[0]
    if temp =='재생':
        driver.find_element_by_xpath('//*[@id="movie_player"]/div[29]/div[2]/div[1]/button').click()
        time.sleep(1)
    else:
        pass
    
# 스크롤 내리기
def scroll_downs(driver):
    last_height = driver.execute_script("return document.body.scrollHeight")

    while True:
        new_height = driver.execute_script("return document.body.scrollHeight")
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(3)
        if new_height == last_height:
                try:
                    driver.execute_script("window.scrollTo(document.body.scrollHeight, 0);")
                except:
                    break
        last_height = new_height

def scroll_down(driver):
    last_page_height = driver.execute_script("return document.documentElement.scrollHeight")
    
    driver.execute_script("window.scrollTo(0, document.documentElement.scrollHeight);")
    time.sleep(2)
    driver.execute_script("window.scrollTo(0,500)")
    time.sleep(3)
    
    while True:
        driver.execute_script("window.scrollTo(0, document.documentElement.scrollHeight);")
        time.sleep(3)
        new_page_height = driver.execute_script("return document.documentElement.scrollHeight")
        print('스크롤 내리기')
        if new_page_height == last_page_height:
            # 중간에 한번 끊기는걸 방지하기위하여 기존 코드는 맨 위로 올렸다가 다시 내리는 작업을 진행함
            # 아래 코드는 한번도 스크롤 내리는 방법
            before_h = driver.execute_script("return window.scrollY")
            driver.find_element_by_css_selector("body").send_keys(Keys.END)
            after_h = driver.execute_script("return window.scrollY")
            if before_h == after_h:
                break 
        last_page_height = new_page_height

            
            
def scroll_downs(driver):
    before_h = driver.execute_script("return window.scrollY")
    
    # 무한 스크롤
    while True:

        # 맨 아래로 스크롤을 내린다.
        driver.find_element_by_css_selector("body").send_keys(Keys.END)
        
        # 스크롤 사이 페이지 로딩 시간
        time.sleep(4)
        
        # 스크롤 후 높이
        after_h = driver.execute_script("return window.scrollY")
        if after_h == before_h:
            break
        before_h = after_h
    
# 시간체크
now = datetime.now()

# 영상정지
play_stop(driver)
    
#스크롤 다운
scroll_down(driver)
time.sleep(1)

# 동영상제목
print('페이지소스 받아오기')
html = driver.page_source
soup = BeautifulSoup(html,'html.parser')
print('페이지소스 통과')
title = soup.find("script",class_='style-scope ytd-player-microformat-renderer').get_text() 

# 구독자 수
counts = soup.find('yt-formatted-string',id='owner-sub-count').get_text()
print(counts)
# 채널명
name = soup.find('div',class_='style-scope ytd-channel-name').find('a',class_='yt-simple-endpoint style-scope yt-formatted-string').get_text()
print(name)

# 조회수
view_counts = soup.find('span',class_='view-count style-scope ytd-video-view-count-renderer').get_text().split(' ')[1]
print('조회수',view_counts)

# 영상 좋아요 수
try:
    good_counts = soup.find('yt-formatted-string',class_='style-scope ytd-toggle-button-renderer style-text').get_text()
except:
    good_counts = soup.find('span',class_='yt-core-attributed-string yt-core-attributed-string--white-space-no-wrap').get_text()
print('좋아요',good_counts)

# 댓글 크롤링
comments = soup.find('ytd-app').find('div',class_='style-scope ytd-app').find('ytd-page-manager',class_='style-scope ytd-app').find('div',id='columns').findAll('ytd-comment-thread-renderer')

number = 0
for comment in comments:
    number += 1 
    #댓글 text
    print('\n')
    text = comment.find('div',{"id":'comment-content','class':'style-scope ytd-comment-renderer'}).get_text().replace('자세히 보기','').replace('간략히','').replace('\n','') .strip()
    print('번호',number)
    print('text',text)
    
    #작성자
    author = comment.find('a',id='author-text').get_text().strip()
    print('작성자',author)
    
    # 공감
    agree_counts = comment.find('span',class_='style-scope ytd-comment-action-buttons-renderer').get_text().strip()
    print('공감',agree_counts)
    
    #시간 크롤링
    original_times = comment.find('a',class_='yt-simple-endpoint style-scope yt-formatted-string').get_text().replace('(수정됨)','').strip()
    print('시간',original_times)
    
    
    #날짜로 변환
    if "년" in original_times:
        year = original_times.split('년')[0]
        times = str(now - relativedelta(years=int(year))).split(" ")[0]
        print("년 단위:",times)
        
    elif "개월" in original_times:
        month = original_times.split('개월')[0]
        times = str(now - relativedelta(months=int(month))).split(" ")[0]       
        print("개월 단위:",times)
        
    elif "주" in original_times:
        month = original_times.split('주')[0]
        times = str(now - relativedelta(weeks=int(month))).split(" ")[0]       
        print("주 단위:",times)
        
    elif "일" in original_times:
        month = original_times.split('일')[0]
        times = str(now - relativedelta(days=int(month))).split(" ")[0]    
        print("일 단위:",times) 
    else:
        times = str(now).split(" ")[0]     
        print("초:",times)
        
print('댓글총 갯수',len(comments))