import csv
import random
from datetime import datetime, timedelta
import time

# CSV 파일명 설정
csv_file_name = './data/real_time_data'

# CSV 파일에 칼럼명 작성
columns = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J']

# 시작 시간을 현재 시간으로 설정
current_time = datetime.now()

# 1초마다 데이터 생성 및 CSV 파일에 추가
cnt = 0
num = 1000
while True:
    # A 열(datetime): 현재 시간 증가
    current_time += timedelta(seconds=1)
    # B~J 열: 랜덤 실수값 생성 (예: 0부터 100 사이의 랜덤 값)
    data_row = [current_time] + [random.uniform(0, 100) for _ in range(9)]
    
    # CSV 파일에 데이터 추가
    with open(csv_file_name + str(num) + '.csv', mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(data_row)
    
    print(f"Data added: {data_row}")
    cnt+=1
    if cnt % 10 == 0:
        num+=1
    
    # 1초 대기
    time.sleep(1)
