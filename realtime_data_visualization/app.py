from flask import Flask, render_template, request, jsonify
import pandas as pd
import os

app = Flask(__name__)

# CSV 파일 경로 설정
csv_directory = '../data'  # 사용자가 실시간 차트에 사용할 CSV 파일 경로 지정
datetime_column = 'A'  # datetime 형 칼럼명 사용자가 지정

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


# 실시간 차트 데이터 읽기
def read_realtime_data(file_path):
    try:
        df = pd.read_csv(file_path)
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
    csv_list = find_csv_files(csv_directory)
    latest_file = sort(key=lambda x: os.path.getmtime(os.path.join(directory, x)), reverse=True)
    
    if latest_file:
        df, numeric_columns = read_realtime_data(latest_file)
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
        return jsonify({'error': 'No CSV files found'})

@app.route('/batch-chart', methods=['POST'])
def batch_chart_data():
    file = request.files['file']
    if file:
        df = pd.read_csv(file)
        df[datetime_column] = pd.to_datetime(df[datetime_column])
        numeric_columns = df.select_dtypes(include=['float64', 'int64']).columns.tolist()
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
