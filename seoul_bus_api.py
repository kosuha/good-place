#-*- coding: utf-8 -*-
import os
import sys
import json
import urllib.request
import pandas as pd
import config.seoul_api as seoul_api

# api key
key = seoul_api.bus_key
# 요청 파일 타입
response_type = "json"

# 서울시 버스노선별 정류장별 승하차 인원 정보
def bus_onoff_data(date):
    start_page = 1
    
    # 빈 DataFrame 만들기
    df = pd.DataFrame(columns=['USE_DT', 'BUS_ROUTE_ID', 'BUS_ROUTE_NO', 'BUS_ROUTE_NM', 'STND_BSST_ID', 'BSST_ARS_NO', 'BUS_STA_NM', 'RIDE_PASGR_NUM', 'ALIGHT_PASGR_NUM', 'WORK_DT'])

    while True:
        # 한번에 가져올 수 있는 데이터 수
        end_page = start_page + 999
        
        # url에 값을 넣고 전송하여 응답을 받아옴
        url = f"http://openapi.seoul.go.kr:8088/{key}/{response_type}/CardBusStatisticsServiceNew/{start_page}/{end_page}/{date}/"
        print(url)
        request = urllib.request.Request(url)
        response = urllib.request.urlopen(request)
        rescode = response.getcode()
        response_body = response.read()
        data_dict_container = json.loads(response_body.decode('utf-8'))

        try:
            # 받은 응답을 변수에 저장
            data_dict = data_dict_container['CardBusStatisticsServiceNew']

            # 응답이 제대로 들어왔을 경우 DataFrame에 한 줄씩 저장 
            if data_dict['RESULT']['CODE'] == 'INFO-000':
                data_list = data_dict['row']
                for row in data_list:
                    row_df = pd.DataFrame([row])
                    df = pd.concat([df, row_df])

                start_page += 1000
                
                # 마지막 페이지인 경우 반복문 탈출
                if data_dict['list_total_count'] < start_page:
                    print("END")
                    print(df)
                    break

            else:
                print(data_dict)
                break

        except Exception as e:
            print(data_dict_container)
            if data_dict_container['RESULT']['CODE'] == 'INFO-200':
                print(data_dict_container['RESULT']['MESSAGE'])
                break

    

bus_onoff_data("20210417")