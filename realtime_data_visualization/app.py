from flask import Flask, render_template, request, jsonify
import pandas as pd
import os
from datetime import datetime

app = Flask(__name__)

# CSV 파일 경로 설정
csv_directory = '../../data'  # 사용자가 실시간 차트에 사용할 CSV 파일 경로 지정
datetime_column = 'SVNA'  # Baco : Timer, Surplus : SVNA

def find_csv_files(folder_path):
    # CSV 파일 경로를 저장할 리스트 초기화
    csv_files = []
    
    # os.walk를 사용하여 폴더와 모든 하위 폴더 탐색
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            # 파일 확장자가 .csv인 경우 리스트에 추가
            if file.endswith('.csv'):
                csv_files.append(os.path.join(root, file))
    
    return csv_files

# 시간 형식을 통일하는 함수 정의
# Baco PVD 1,2,3 : [2024.08.27 14:10:18]
# Baco Wafer History 2024-08-27_10:23:51.800
# GSF surplus : 2024-07-30 17:00:03
# RETURN : %Y-%m-%d %H:%M:%S.%f
def unify_datetime_format(date_str):
    # 여러 가지 가능한 시간 형식을 정의
    formats = [
        "[%Y.%m.%d %H:%M:%S]",          # 형식: [2024.08.27 14:10:18]
        "%Y-%m-%d_%H:%M:%S.%f",       # 형식: 2024-08-27_10:23:51.800
        "%Y-%m-%d %H:%M:%S",           # 형식: 2024-07-30 17:00:03
        "%Y-%m-%d %H:%M:%S.%f"           # 형식: 2024-07-30 17:00:03.123231
    ]
    for fmt in formats:
        try:
            if type(date_str) != type("asd"):
                formatted_time_str = dt.strftime(fmt)
            # 각 형식으로 변환 시도
            dt = datetime.strptime(date_str, fmt)
            # 변환 성공 시 미세초를 소수점 3자리까지 유지하여 문자열로 반환
            return dt.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
        except ValueError:
            continue

    # 만약 모든 형식이 실패할 경우 원본 문자열 반환 (또는 에러 처리)
    return date_str

# 실시간 차트 데이터 읽기
def read_realtime_data(file_path, time_col="None"):
    try:
        if time_col == 'SVID' or time_col == 'VID' or time_col == 'SVNA' or time_col == 'UNIT':
            usecols = [0] + list(range(531, 631, 9))
            df = pd.read_csv(file_path, header=2, skiprows=[3], usecols=usecols)
        else:
            df = pd.read_csv(file_path)
        # 데이터를 통일된 형식으로 변환
        df[datetime_column] = df[datetime_column].apply(unify_datetime_format)
        df[datetime_column] = pd.to_datetime(df[datetime_column])
        numeric_columns = df.select_dtypes(include=['float64', 'int64']).columns.tolist()
        return df, numeric_columns
    except Exception as e:
        print(f"Error reading file: {e}")
        return None, []

@app.route('/')
def index():
    return render_template('layout.html', title="KETI 반도체 장비 데이터 시각화")

@app.route('/realtime-chart')
def realtime_chart():
    return render_template('realtime_chart.html', title="실시간 차트")

@app.route('/batch-chart')
def batch_chart():
    return render_template('batch_chart.html', title="배치파일 차트")

@app.route('/realtime-data', methods=['GET'])
def get_realtime_data():
    latest_file = find_csv_files(csv_directory)
    latest_file.sort(key=lambda x: os.path.getmtime(x), reverse=True)
    latest_file = latest_file[0]
    if latest_file:
        df, numeric_columns = read_realtime_data(latest_file, datetime_column)
        if df is not None:
            data = []
            for column in numeric_columns:
                trace = {
                    'x': df[datetime_column].astype(str).tolist(),
                    'y': df[column].tolist(),
                    'type': 'scatter',
                    'mode': 'lines',
                    'name': column
                }
                data.append(trace)
            layout = {
                'title': '실시간 차트',
                'xaxis': {'rangeslider': {'visible': True}},
                'yaxis': {'title': 'Values'},
            }
            return jsonify({'data': data, 'layout': layout})
        else:
            return jsonify({'error': 'Error reading the CSV file'})
    else:
        return jsonify({'error': 'No CSV files found'})

@app.route('/batch-chart', methods=['POST'])
def batch_chart_data():
    file = request.files['file']
    if file:
        df, numeric_columns = read_realtime_data(file, datetime_column)
        data = []
        for column in numeric_columns:
            trace = {
                'x': df[datetime_column].astype(str).tolist(),
                'y': df[column].tolist(),
                'type': 'scatter',
                'mode': 'lines',
                'name': column
            }
            data.append(trace)
        layout = {
            'title': '배치파일 차트',
            'xaxis': {'rangeslider': {'visible': True}},
            'yaxis': {'title': 'Values'},
        }
        return jsonify({'data': data, 'layout': layout})
    else:
        return jsonify({'error': 'File upload failed'})

if __name__ == '__main__':
    app.run(debug=True)