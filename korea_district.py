import openpyxl
import pandas as pd
import pymysql
from sqlalchemy import create_engine
import config.conn as pw

# DB에 연결
engine = create_engine(pw.conn)
conn = engine.connect()

# 시작과 끝 설정
start_row = 6
end_row = 3797

district_list = []

# 엑셀 파일 열기
print("file loading...")
wb = openpyxl.load_workbook('korea_district_202104.xlsx')
print("file opened!")

# 시트 선택
sheet = wb['1. 총괄표(현행)']

# 배열에 담기
for row in range(start_row, end_row + 1):
    couple_of_value = [sheet[f'E{row}'].value, sheet[f'G{row}'].value]
    if couple_of_value[0] != None and couple_of_value[1] != None:
        district_list.append(couple_of_value)

# DataFrame으로 변환
df = pd.DataFrame(data=district_list, index=range(0, len(district_list)), columns=['si_gun_gu', 'eup_myun_dong'])
print(df)

# DB에 저장
df.to_sql(name='korea_district', con=engine, if_exists='replace', index=True)
print("DB saved!")