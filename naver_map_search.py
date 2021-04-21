#-*- coding: utf-8 -*-

from selenium import webdriver    # 라이브러리에서 사용하는 모듈만 호출
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys    # 키보드 사용
from selenium.webdriver.support.ui import WebDriverWait   # 해당 태그를 기다림
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException    # 태그가 없는 예외 처리
import pandas as pd
import time
import urllib

chromedriver = '/Users/seonhokim/good-place/chromedriver'
options = webdriver.ChromeOptions()
options.add_argument('headless')    # headless chrome 옵션 적용
options.add_argument('disable-gpu')    # GPU 사용 안함
options.add_argument('lang=ko_KR')    # 언어 설정
driver = webdriver.Chrome(chromedriver, options=options) # 옵션 적용

def crawler(si_gun_gu, eup_myun_dong, keyword):
    search_input = urllib.parse.quote(f"{si_gun_gu} {eup_myun_dong} {keyword}") # 한글 깨짐 방지
    search_iframe_tag= 'searchIframe' # 검색결과 iFrame
    entry_iframe_tag = 'entryIframe' # 세부정보 iFrame
    search_title_tag = "Ow5Yt" # 검색결과 class
    next_button_tag = "._2ky45>a:last-child" # 다음페이지 버튼 css selector
    last_page_tag = "._2ky45>a:nth-last-child(2)" # 마지막 페이지 버튼 css selector

    url = "https://map.naver.com/v5/search/" + search_input + "?c=14117202.5271319,4542958.3391012,12,0,0,0,dh"

    print("-" * 100)

    driver.get(url) # 크롤링할 사이트 호출
    print(url)
    
    # 검색결과 프레임으로 전환
    search_frame = driver.find_element_by_id(search_iframe_tag) 
    driver.switch_to.frame(search_frame)

    try:
        # 3초간 로딩 대기
        element = WebDriverWait(driver, 3).until(
            EC.presence_of_element_located((By.CLASS_NAME, search_title_tag))
        )

        count = 1
        page_count = 1
        store_list = []

        # 페이지별 크롤링
        while True:
            # 스크롤 박스를 선택하고 끝까지 스크롤 다운해서 모든 정보 로딩
            body = driver.find_element_by_css_selector('body')
            next_button = driver.find_element_by_css_selector(next_button_tag)
            element = driver.find_element_by_class_name('_1Az1K')
            element.click()
            for i in range(0, 30):
                body.send_keys(Keys.PAGE_DOWN)
                time.sleep(0.5)
            time.sleep(1)

            # 타이틀을 클릭하여 세부정보를 불러온 후 크롤링
            search_elements = driver.find_elements_by_class_name(search_title_tag)
            for button in search_elements:
                # 타이틀 클릭
                button.send_keys(Keys.ENTER)
                time.sleep(1)

                # 세부정보 iFrame으로 전환
                driver.switch_to.default_content()
                entry_frame = driver.find_element_by_id(entry_iframe_tag)
                driver.switch_to.frame(entry_frame)
                time.sleep(1)

                # 상호명, 업종, 주소, 전화번호(없으면 공백) 크롤링
                title = driver.find_element_by_css_selector('#_title>span:nth-child(1)').text
                sector = driver.find_element_by_css_selector('#_title>span:nth-child(2)').text
                address = driver.find_element_by_class_name('_2yqUQ').text
                try:
                    phone_number = driver.find_element_by_class_name('_3ZA0S').text
                except:
                    phone_number = ''
                
                # 리스트에 추가
                store_list.append([title, sector, address, phone_number])
                print(count, [title, sector, address, phone_number])
                count += 1

                # 검색결과 iFrame으로 전환
                driver.switch_to.default_content()
                search_frame = driver.find_element_by_id(search_iframe_tag)
                driver.switch_to.frame(search_frame)

            time.sleep(1)

            # 다음페이지로 넘어가기
            next_button.click()
            time.sleep(1)

            # 현재 마지막 페이지인 경우 반복문 탈출
            last_page_num = int(driver.find_element_by_css_selector(last_page_tag).text)
            if page_count != last_page_num:
                page_count += 1
            else:
                break
        
        # DataFrame으로 변환
        df = pd.DataFrame(data=store_list, index=range(0, len(store_list)), columns=['title', 'sector', 'address', 'phone_number'])
        print(df)

        # 드라이버 종료
        driver.quit()

        return df

    # 예외처리
    except TimeoutException:
        print('해당 페이지에 정보가 존재하지 않습니다.')
        driver.quit()

    print("-" * 100)

crawler("파주시", "광탄면", "카페")

