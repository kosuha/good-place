#-*- coding: utf-8 -*-
import os
import sys
import json
import urllib.request
import pandas as pd
import config.api_keys as api
import config.conn as pw
import pymysql
from sqlalchemy import create_engine

# DB에 연결
db_connection = create_engine(pw.conn)
conn = db_connection.connect()

# api key
key = api.seoul_bus_key
# 요청 파일 타입
response_type = "json"

# 서울시 버스노선별 정류장별 승하차 인원 정보
def bus_onoff_data(date):
    start_page = 1
    
    # 빈 DataFrame 만들기
    dfs = []
    
    while True:
        # 한번에 가져올 수 있는 데이터 수
        end_page = start_page + 999
        
        # url에 값을 넣고 전송하여 응답을 받아옴
        url = f"http://openapi.seoul.go.kr:8088/{key}/{response_type}/CardBusStatisticsServiceNew/{start_page}/{end_page}/{date}/"
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
            data_dict = data_dict_container['CardBusStatisticsServiceNew']

            # 응답이 제대로 들어왔을 경우 DataFrame에 한 줄씩 저장 
            if data_dict['RESULT']['CODE'] == 'INFO-000':
                data_list = data_dict['row']
                page_df = pd.DataFrame(columns=[
                    'USE_DT',
                    'BUS_ROUTE_ID',
                    'BUS_ROUTE_NO',
                    'BUS_ROUTE_NM',
                    'STND_BSST_ID',
                    'BSST_ARS_NO',
                    'BUS_STA_NM',
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

# 버스정류장별 하차 승객 수의 합
def bus_off_sum(date):
    bus_onoff = pd.read_sql_query("select * from test", db_connection) # 테스트용
    # bus_onoff = bus_onoff_data(date)

    # 필요한 colume만 추출
    bus_off = bus_onoff[['STND_BSST_ID', 'ALIGHT_PASGR_NUM']]
    bus_stops = bus_off['STND_BSST_ID'].to_list()
    bus_stops = list(set(bus_stops)) # 중복 제거
    off_passengers_nums = []

    # 정류장별로 합계 구해서 배열에 추가
    for stop in bus_stops:
        is_stop = bus_off['STND_BSST_ID'] == stop
        bus_off_for_stop = bus_off[is_stop]
        off_passengers_nums.append(bus_off_for_stop['ALIGHT_PASGR_NUM'].sum())

    # DataFrame으로 변환
    df = pd.DataFrame({'STND_BSST_ID': bus_stops, 'ALIGHT_PASGR_NUM': off_passengers_nums})
    print(df)

bus_off_sum("20210416")