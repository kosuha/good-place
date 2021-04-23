#-*- coding: utf-8 -*-
import os
import sys
import json
import urllib.request
import pandas as pd
import config.seoul_api_keys as seoul_api
import config.conn as pw
import pymysql
from sqlalchemy import create_engine

# DB에 연결
db_connection = create_engine(pw.conn)
conn = db_connection.connect()

# api key
key = seoul_api.subway_key
# 요청 파일 타입
response_type = "json"

# 서울시 지하철호선별 역별 승하차 인원 정보
def subway_onoff_data(date):
    start_page = 1
    
    # 빈 DataFrame 만들기
    dfs = []
    
    while True:
        # 한번에 가져올 수 있는 데이터 수
        end_page = start_page + 999
        
        # url에 값을 넣고 전송하여 응답을 받아옴
        url = f"http://openapi.seoul.go.kr:8088/{key}/{response_type}/CardSubwayStatsNew/{start_page}/{end_page}/{date}/"
        print(url)

        # 가끔씩 이 부분에서 urllib.error.URLError: <urlopen error [Errno 60] Operation timed out> 발생
        # 에러 발생시 다시 시도
        try:
            request = urllib.request.Request(url)
            response = urllib.request.urlopen(request)
            rescode = response.getcode()
            response_body = response.read()
            data_dict_container = json.loads(response_body.decode('utf-8'))
        except Exception as e:
            print(e)
            continue

        try:
            # 받은 응답을 변수에 저장
            data_dict = data_dict_container['CardSubwayStatsNew']

            # 응답이 제대로 들어왔을 경우 DataFrame에 한 줄씩 저장 
            if data_dict['RESULT']['CODE'] == 'INFO-000':
                data_list = data_dict['row']
                page_df = pd.DataFrame(columns=[
                    'USE_DT',
                    'LINE_NUM',
                    'SUB_STA_NM',
                    'RIDE_PASGR_NUM',
                    'ALIGHT_PASGR_NUM',
                    'WORK_DT'
                ])

                for row in data_list:
                    row_df = pd.DataFrame([row])
                    page_df = pd.concat([page_df, row_df])

                dfs.append(page_df)
                start_page += 1000
                
                # 마지막 페이지인 경우 반복문 탈출
                if data_dict['list_total_count'] < start_page:
                    print("END")
                    df = pd.concat(dfs)
                    # df.to_sql(name='test', con=db_connection, if_exists='replace', index=False) # 테스트용
                    return df

            else:
                print(data_dict)
                break

        except Exception as e:
            print(data_dict_container)
            if data_dict_container['RESULT']['CODE'] == 'INFO-200':
                print(data_dict_container['RESULT']['MESSAGE'])
                break

# 지하철역별 하차 승객 수의 합
def subway_off_sum(date):
    # subway_onoff = pd.read_sql_query("select * from test", db_connection) # 테스트용
    subway_onoff = subway_onoff_data(date)

    # 필요한 colume만 추출
    subway_off = subway_onoff[['SUB_STA_NM', 'ALIGHT_PASGR_NUM']]
    subway_stations = subway_off['SUB_STA_NM'].to_list()
    subway_stations = list(set(subway_stations)) # 중복 제거
    off_passengers_nums = []

    # 정류장별로 합계 구해서 배열에 추가
    for station in subway_stations:
        is_station = subway_off['SUB_STA_NM'] == station
        subway_off_for_station = subway_off[is_station]
        off_passengers_nums.append(subway_off_for_station['ALIGHT_PASGR_NUM'].sum())

    # DataFrame으로 변환
    df = pd.DataFrame({'SUB_STA_NM': subway_stations, 'ALIGHT_PASGR_NUM': off_passengers_nums})
    print(df)

subway_off_sum("20210416")