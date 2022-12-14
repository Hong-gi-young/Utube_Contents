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
from utube import *
from shorts import shorts_crawling
import urllib


chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument('--headless')
chrome_options.add_argument('--no-sandbox')
chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
chrome_options.add_argument('--disable-gpu')  
driver = webdriver.Chrome('chromedriver.exe', chrome_options=chrome_options)

def uploaded_videos(sorting_value):
    #정렬기준 선택
    try:
        driver.find_element_by_xpath('//*[@id="sort-menu"]/yt-sort-filter-sub-menu-renderer/yt-dropdown-menu').click()
        time.sleep(1)
    except:
        driver.find_element_by_link_text('정렬 기준').click()
        time.sleep(1)

    driver.find_element_by_link_text(sorting_value).click()
    time.sleep(1)

def videos_select_options(sorting_value='인기 동영상',selected_options='업로드한 동영상'):
    
    # 업로드된 동영상 칸 클릭
    driver.find_element_by_xpath('//*[@id="primary-items"]/yt-dropdown-menu').click()
    time.sleep(1)
    try:
        driver.find_element_by_link_text(selected_options).click()
        time.sleep(1)
        if selected_options == '업로드한 동영상':
            #정렬기준 설정
            uploaded_videos(sorting_value)
    except:
        uploaded_videos(sorting_value)
        time.sleep(1)
        
# 스크롤 내리기
def scroll_down():
    
    # 스크롤 높이 가져옴
    last_height = driver.execute_script("return document.documentElement.scrollHeight")
    print('last_height',last_height)
    while True:
        # 끝까지 스크롤 다운
        driver.execute_script("window.scrollTo(0, 200000);")

        # 1초 대기
        time.sleep(1)

        # 스크롤 다운 후 스크롤 높이 다시 가져옴
        new_height = driver.execute_script("return document.documentElement.scrollHeight")
        print('new_height',new_height)
        if new_height == last_height:
            break
        last_height = new_height

def total_video_crawling(user_url = "https://www.youtube.com/c/DickHunter/featured",crawling_count=np.inf):

    url_splited = user_url.split('/')
    if url_splited[-1] =='featured':
        user_url = user_url.replace('featured', 'videos') 
    
    elif 'videos' not in url_splited:
        user_url = user_url + '/'+ 'videos'
        
    driver.get(user_url) 
    time.sleep(4)
    
    # 업로드한 영상 + 정렬기준
    videos_select_options()

    urls = [] # 전체 url 리스트
    original_url = [] # 일반 동영상 url
    shorts_url = [] # shorts 동영상 url
    total_df = pd.DataFrame()
    soup = soup_find(driver)

    #구독자수
    counts = soup.find('yt-formatted-string',{'id':'subscriber-count','class':'style-scope ytd-c4-tabbed-header-renderer'}).get_text().replace('구독자','').strip()
    print('구독자 수:',counts)

    #영상 수
    information_all = soup.find('div',{'id':'contents','class':'style-scope ytd-item-section-renderer'}).find_all('ytd-grid-video-renderer',class_='style-scope ytd-grid-renderer')

    #갯수 파악
    if crawling_count > len(information_all):
        print('갯수 미달로 인한 스크롤')
        scroll_down() # 스크롤 한번씩 내리기
        
    # URL 수집
    soup = soup_find(driver)
    information_all = soup.find('div',{'id':'contents','class':'style-scope ytd-item-section-renderer'}).find_all('ytd-grid-video-renderer',class_='style-scope ytd-grid-renderer')
    for idx,inform in enumerate(information_all):
        #url
        url = inform.find('a',class_='yt-simple-endpoint inline-block style-scope ytd-thumbnail')['href']
        url = "https://www.youtube.com"+url
        urls.append(url)

        idx = idx+1 
        if crawling_count == idx: 
            break
        
    for url in urls:
        print(f'{url} 동영상 크롤링 시작')
        if 'shorts' in url:
            try:
                df = shorts_crawling(url)
                shorts_url.append(url) #shorts만 따로 담기
                df['구독자'] = counts
                df['영상구분'] = 'shorts'
            except:
                continue
        else:
            df = one_crawling(url) 
            original_url.append(url) #일반동영상 따로 담기
            df['영상구분'] = 'video'
            
        # concat 실행
        total_df = pd.concat([total_df,df])
        print('\n')
    print('shorts_url',shorts_url, len(shorts_url))
    total_df.to_excel('total_df.xlsx')
    driver.close()

if __name__ == "__main__":
    total_video_crawling(user_url ="https://www.youtube.com/c/%EC%88%A0%EC%A3%BC%EC%84%9C%EC%A3%BCsoju")