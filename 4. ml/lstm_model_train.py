import os
import time
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MinMaxScaler
# os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'
os.environ["CUDA_VISIBLE_DEVICES"] = "0"
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense
import matplotlib.pyplot as plt
from sklearn.metrics import accuracy_score, confusion_matrix, precision_score, recall_score, f1_score, roc_auc_score


# 함수: LSTM 모델을 위한 데이터셋 생성
def create_dataset(X, y, time_steps=1):
    Xs, ys = [], []
    for i in range(len(X) - time_steps):
        v = X.iloc[i:(i + time_steps)].values
        Xs.append(v)
        ys.append(y[i + time_steps])
    return np.array(Xs), np.array(ys)


def create_dataset_add_dense(X, y, time_steps=1, n_future=1):
    Xs, ys = [], []
    for i in range(len(X) - time_steps - n_future + 1):
        v = X.iloc[i:(i + time_steps)].values
        Xs.append(v)
        ys.append(y[i + time_steps:i + time_steps + n_future])  # 여러 시점을 예측
    return np.array(Xs), np.array(ys)


# 함수 : 디렉토리 서칭
def recursive_search_dir(_nowDir, _filelist, _form='csv'):
    dir_list = []  # 현재 디렉토리의 서브디렉토리가 담길 list
    if _nowDir[-1] == '/':
        _nowDir = _nowDir[0:-1]
    f_list = os.listdir(_nowDir)
    for fname in f_list:
        if os.path.isdir(_nowDir + "/" + fname):
            dir_list.append(_nowDir + "/" + fname)
        elif os.path.isfile(_nowDir + "/" + fname):
            file_extension = os.path.splitext(fname)[1]
            if file_extension == '.' + _form.lower() or file_extension == '.' + _form.upper():  # csv
                _filelist.append(_nowDir + "/" + fname)

    for toDir in dir_list:
        recursive_search_dir(toDir, _filelist, _form)


def evaluate_model(_df, test_data_df, predict_col_num, _dense, _time_steps, _epochs, _batch_size):
    start_time = time.time()
    # 정규화를 위해 MinMaxScaler 사용
    scaler = MinMaxScaler()
    data_scaled = scaler.fit_transform(_df)

    # LSTM에 필요한 데이터 형태로 데이터셋 생성
    if _dense == 1:
        X, y = create_dataset(pd.DataFrame(data_scaled), data_scaled[:, predict_col_num], _time_steps)
    else:
        X, y = create_dataset_add_dense(pd.DataFrame(data_scaled), data_scaled[:, predict_col_num], _time_steps, _dense)
    
    # 데이터셋을 훈련 세트와 테스트 세트로 분할
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42, shuffle=False)

    # LSTM 모델 구축
    model = Sequential([
        LSTM(50, input_shape=(X_train.shape[1], X_train.shape[2])),
        Dense(_dense)
    ])

    # 모델 컴파일
    model.compile(optimizer='adam', loss='mean_squared_error', metrics=['mean_absolute_error'])

    # 모델 훈련
    history = model.fit(
        X_train, y_train,
        epochs=_epochs,
        batch_size=_batch_size,
        validation_split=0.1,
        verbose=1,
        shuffle=False
    )
    print(f'\n\n================== train time : {time.time()-start_time} ==================\n')
    
    # 전체 데이터 테스트를 위한 데이터셋
    data_scaled2 = scaler.fit_transform(test_data_df)

    if _dense == 1:
        test_x, test_y = create_dataset(pd.DataFrame(data_scaled2), data_scaled2[:, predict_col_num], _time_steps)
    else:
        test_x, test_y = create_dataset_add_dense(pd.DataFrame(data_scaled2), data_scaled2[:, predict_col_num], _time_steps, _dense)

    y_pred = model.predict(test_x)
    
    # 모델 평가
    test_loss, test_acc = model.evaluate(test_x, test_y, verbose=0)

    print('\n\n================== 모델 평가 결과 ====================')
    print(f'\nMAE: {test_acc}, loss(MSE): {test_loss}')
    
    model_path = 'LSTM_'+str(_dense)+'_'+str(_time_steps)+'_'+str(_epochs)+'_'+str(_batch_size)+'.h5'
    model.save(model_path)
    
    return test_loss, test_acc, test_x, test_y, y_pred

if __name__ == '__main__':
    _dense = 1
    _epochs = 100
    _batch_size = 16
    _time_steps = 60
    predict_col_num = 10  # 예측하고자 하는 컬럼의 인덱스(0부터 시작)

    file_name = ''
    time_field = ''
    # 학습 데이터 셋
    df = pd.read_csv(file_name)
    df = df.drop([time_field], axis=1)
    df = df.dropna(axis=0)

    # 테스트 데이터셋
    test_df = pd.read_csv(file_name)
    test_df = test_df.drop([time_field], axis=1)
    test_df = test_df.dropna(axis=0)

    # accuracies = []
    # losses = []

 
    print("\n\n===============================================================================================================")
    print(f"\n인자값 정보 : dense : {_dense}, epoch : {_epochs}, batch size : {_batch_size}, sequence length : {_time_steps}")

    loss, acc, test_x, test_y, y_pred = evaluate_model(df, test_df, predict_col_num, _dense, _time_steps, _epochs, _batch_size)