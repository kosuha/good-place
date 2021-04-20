#-*- coding: utf-8 -*-

from selenium import webdriver    # 라이브러리에서 사용하는 모듈만 호출
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait   # 해당 태그를 기다림
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException    # 태그가 없는 예외 처리
from selenium.webdriver.common.action_chains import ActionChains
import pandas as pd
import time
import urllib
import webbrowser

chromedriver = '/Users/seonhokim/good-place/chromedriver'
options = webdriver.ChromeOptions()
options.add_argument('headless')    # headless chrome 옵션 적용
options.add_argument('disable-gpu')    # GPU 사용 안함
options.add_argument('lang=ko_KR')    # 언어 설정
driver = webdriver.Chrome(chromedriver) # 옵션 적용

si_gun_gu = "파주시"
eup_myun_dong = "광탄면"
sector = "카페"
search_input = urllib.parse.quote(f"{si_gun_gu} {eup_myun_dong} {sector}") # 한글 깨짐 방지
iframe_tag= 'searchIframe'
name_tag = "_3Yilt" # 카페명 class
next_button_tag = "._2ky45>a:last-child" # 다음페이지 버튼 css selector

url = "https://map.naver.com/v5/search/" + search_input + "?c=14117202.5271319,4542958.3391012,12,0,0,0,dh"

print("-" * 100)

driver.get(url) # 크롤링할 사이트 호출
print(url)
frame = driver.find_element_by_id(iframe_tag)
driver.switch_to.frame(frame)

try:
    element = WebDriverWait(driver, 3).until(
        EC.presence_of_element_located((By.CLASS_NAME, name_tag))
    )
    print("크롤링 중...")

    name_list = []
    while True:
        body = driver.find_element_by_css_selector('body')
        next_button = driver.find_element_by_css_selector(next_button_tag)
        element = driver.find_element_by_class_name('_2lx2y')
        mouse_over = ActionChains(driver).move_to_element(element)
        mouse_over.perform()

        for i in range(0, 17):
            body.send_keys(Keys.PAGE_DOWN)
            time.sleep(0.5)
        
        time.sleep(1)
        name_list += driver.find_elements_by_class_name(name_tag)
        
        try:
            next_button.click()
        except:
            print("데이터 수집 완료! \n")
            break

    for i in name_list:
        print(i.text)

except TimeoutException:
    print('해당 페이지에 정보가 존재하지 않습니다.')

finally:
    driver.quit()

print("-" * 100)

