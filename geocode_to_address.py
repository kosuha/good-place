import os
import sys
import json
import urllib.request
import config.api_keys as api

# api key
key = api.kakao_key

# 좌표를 받아 [시군구, 읍면동]을 반환
def geocoder(x, y):
    # url에 값을 넣고 전송하여 응답을 받아옴
    url = f"https://dapi.kakao.com/v2/local/geo/coord2regioncode.json?x={x}&y={y}"
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
        address = [data_dict[0]['region_2depth_name'], data_dict[0]['region_3depth_name']]
        print(address)
        return address
    except Exception as e:
        print(e)
        print(data_dict)

geocoder(127.1273370925, 37.5403430618)