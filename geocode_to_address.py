import os
import sys
import json
import urllib.request
import config.seoul_api_keys as seoul_api

# api key
key = seoul_api.vworld_key
# 요청 파일 타입
response_type = "json"

# 좌표를 받아 시군구, 읍면동을 반환
def geocoder(x, y):
    # url에 값을 넣고 전송하여 응답을 받아옴
    url = f"http://api.vworld.kr/req/address?service=address&request=getAddress&version=2.0&crs=epsg:4326&point={x},{y}&format={response_type}&type=ROAD&zipcode=false&simple=true&key={key}"
    print(url)

    # 가끔씩 이 부분에서 urllib.error.URLError: <urlopen error [Errno 60] Operation timed out> 발생
    # 에러 발생시 다시 시도
    while True:
        try:
            request = urllib.request.Request(url)
            response = urllib.request.urlopen(request)
            rescode = response.getcode()
            response_body = response.read()
            data_dict_container = json.loads(response_body.decode('utf-8'))
            break
        except Exception as e:
            print(e)
            continue
    
    data_dict = data_dict_container['response']

    try:
        address = [data_dict['result'][0]['structure']['level2'], data_dict['result'][0]['structure']['level4A']]
        print(address)
    except Exception as e:
        print(e)
        print(data_dict)