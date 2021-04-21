import naver_api
import naver_map_search

# naver_map_search.crawler("파주시", "광탄면", "카페")

setting = {
        "startDate": "2017-01-01",
        "endDate": "2017-04-30",
        "timeUnit": "month",
        "keywordGroups":
            [
                {
                    "groupName": "한글",
                    "keywords": ["한글", "korean"]
                },
                {
                    "groupName": "영어",
                    "keywords": ["영어", "english"]
                }
            ],
        "ages": ["1", "2"],
        "gender": "f"
    }

naver_api.search_trend(setting)
