#-*- coding: utf-8 -*-
import os
import sys
import json
import urllib.request
import urllib.parse
import pandas as pd
import config.api_keys as api
import seoul_subway_api

# api key
key = api.kakao_key

df = seoul_subway_api.subway_off_sum('20201111')

# 역 이름으로 주소 받아오기
def get_address(station_name_):
    # 괄호 지우기
    station_name = station_name_
    is_parenthesis = station_name.find('(')
    if is_parenthesis != -1:
        station_name = station_name[0:is_parenthesis]
    
    station_name += "역"

    # 한글 깨짐 방지
    station_name = urllib.parse.quote(station_name)
    # url에 값을 넣고 전송하여 응답을 받아옴
    url = f"https://dapi.kakao.com/v2/local/search/keyword.json?page=1&size=15&sort=accuracy&category_group_code=SW8&query={station_name}"
    print(url)

    # 가끔씩 이 부분에서 urllib.error.URLError: <urlopen error [Errno 60] Operation timed out> 발생
    # 에러 발생시 다시 시도
    while True:
        try:
            request = urllib.request.Request(url)
            request.add_header("Authorization", key)
            response = urllib.request.urlopen(request)
            rescode = response.getcode()
            response_body = response.read()
            data_dict_container = json.loads(response_body.decode('utf-8'))
            break
        except Exception as e:
            print(e)
            continue

    data_dict = data_dict_container['documents']

    try:
        address = data_dict[0]['address_name']
        return address
    except Exception as e:
        print(e)
        print(data_dict)

