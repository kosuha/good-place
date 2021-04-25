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
import geocode_to_address

# DB에 연결
db_connection = create_engine(pw.conn)
conn = db_connection.connect()

# api key
key = api.seoul_bus_stop_location_key

# 요청 파일 타입
response_type = "json"

# 서울 버스정류장의 위경도 값을 받아오는 api
def get_locations():
    start_page = 1
    
    # 빈 DataFrame 만들기
    dfs = []

    while True:
        # 한번에 가져올 수 있는 데이터 수
        end_page = start_page + 999
        
        # url에 값을 넣고 전송하여 응답을 받아옴
        url = f"http://openapi.seoul.go.kr:8088/{key}/{response_type}/busStopLocationXyInfo/{start_page}/{end_page}/"
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
            data_dict = data_dict_container['busStopLocationXyInfo']

            # 응답이 제대로 들어왔을 경우 DataFrame에 한 줄씩 저장 
            if data_dict['RESULT']['CODE'] == 'INFO-000':
                data_list = data_dict['row']
                page_df = pd.DataFrame(columns=[
                    'STOP_NO',
                    'STOP_NM',
                    'XCODE',
                    'YCODE'
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
                    print(df)
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

    return 0

def add_address():
    df = get_locations()
    addresses = []

    for i in range(0, len(df)):
        xcode = df.iloc[i, 2]
        ycode = df.iloc[i, 3]
        addresses.append(geocode_to_address.geocoder(xcode, ycode))

    df['ADDRESS'] = addresses
    print(df)
    
    return df

# add_address()
