#-*- coding: utf-8 -*-
import os
import sys
import json
import urllib.request
import config.api_keys as api

client_id = api.naver_client_id
client_secret = api.naver_client_secret
url = "https://openapi.naver.com/v1/datalab/search"

# 네이버 통합 검색어 트랜드
def search_trend(setting):
    body = json.dumps(setting, indent = 4)

    request = urllib.request.Request(url)
    request.add_header("X-Naver-Client-Id", client_id)
    request.add_header("X-Naver-Client-Secret", client_secret)
    request.add_header("Content-Type", "application/json")
    response = urllib.request.urlopen(request, data=body.encode("utf-8"))
    rescode = response.getcode()

    if rescode == 200:
        response_body = response.read()
        result = response_body.decode('utf-8')
        print(result)
        return result
    else:
        print("Error Code:" + rescode)
        return -1