import socket
import os
import time
from datetime import datetime, timedelta
import pickle
import logging  # logging 모듈 임포트


# 로그 설정
logging.basicConfig(filename='log.txt', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')


# 지정한 디렉토리에 있는 파일을 검색하여 리스트로 반환
def recursive_search_dir(_nowDir, _filelist):
    dir_list = []  # 현재 디렉토리의 서브디렉토리가 담길 list
    f_list = os.listdir(_nowDir)
    for fname in f_list:
        full_path = os.path.join(_nowDir, fname)
        if os.path.isdir(full_path):
            dir_list.append(full_path)
        elif os.path.isfile(full_path):
            file_extension = os.path.splitext(fname)[1]
            file_extension = os.path.splitext(fname)[1]
            if file_extension == ".csv":
                _filelist.append(full_path)

    for toDir in dir_list:
        recursive_search_dir(toDir, _filelist)


# checked_files를 파일로 저장하는 함수
def save_checked_files(file_data, file_path='checked_files.pkl'):
    with open(file_path, 'wb') as f:
        pickle.dump(file_data, f)

# checked_files를 파일에서 로드하는 함수
def load_checked_files(file_path='checked_files.pkl'):
    if os.path.exists(file_path):
        with open(file_path, 'rb') as f:
            return pickle.load(f)
    return {}


def send_file(file_path, client_socket):
    try:
        # 파일명 전송
        print(f"서버에 파일명 전송 : {file_path}")
        logging.info(f"서버에 파일명 전송 : {file_path}")
        client_socket.sendall(f"FILENAME:{file_path}".encode())

        # 서버가 파일명 수신을 완료했는지 확인
        response = client_socket.recv(1024).decode()
        if response != 'READY':
            print(f"서버가 파일명 수신을 완료하지 못했습니다: {response}")
            logging.error(f"서버가 파일명 수신을 완료하지 못했습니다: {response}")
            return
        print(f"서버 파일명 수신 완료: {response}")
        logging.info(f"서버 파일명 수신 완료: {response}")

        # 파일 데이터 전송
        with open(file_path, 'rb') as file:
            data = file.read()
            client_socket.sendall(data)

        # 파일 데이터 전송이 끝났음을 알리는 빈 바이트 전송
        client_socket.sendall(b'EOF')

        print(f"파일 전송 성공: {file_path}")
        logging.info(f"파일 전송 성공: {file_path}")
    except Exception as e:
        print(f"파일 전송 실패: {file_path} : {e}")
        logging.error(f"파일 전송 실패: {file_path} : {e}")
        
        
if __name__ == '__main__':
    # 서버 정보 설정
    HOST = '192.168.0.2'
    PORT = 5001
    src_local_path = './data'
    src_local_path = os.path.normpath(src_local_path)
    at_least = timedelta(hours=24)  # 파일이 수정된 지 at_least만큼 지난 경우 전송 제외
                                    # days, hours, minutes, seconds
    checked_files = load_checked_files()
    # 소켓 생성 및 서버에 연결
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    try:
        client_socket.connect((HOST, PORT))
        print("\n서버에 연결 성공")
        logging.info("서버에 연결 성공")
    except Exception as e:
        print(f"\n서버에 연결 실패: {e}")
        logging.error(f"서버에 연결 실패: {e}")
        exit()

    while True:
        try:
            # 현재 시간 계산
            now = datetime.now()

            # 파일 목록 검색
            file_list = []
            recursive_search_dir(src_local_path, file_list)

            for file_path in file_list:
                file_size = os.path.getsize(file_path)
                file_mtime = datetime.fromtimestamp(os.path.getmtime(file_path))

                # 이미 전송한 파일인지 확인
                if file_path in checked_files.keys():
                    last_size = checked_files[file_path]['size']
                    last_mtime = checked_files[file_path]['mtime']
    
                    # 파일이 수정된 지 at_least만큼 지난 경우 전송 제외
                    if now - file_mtime > at_least:
                        continue

                    # 파일 크기가 증가했을 때만 전송
                    if file_size > last_size:
                        send_file(file_path, client_socket)
                        checked_files[file_path] = {'size': file_size, 'mtime': file_mtime}
                    else:
                        continue
                else:
                    # 새로운 파일일 경우 전송
                    send_file(file_path, client_socket)
                    checked_files[file_path] = {'size': file_size, 'mtime': file_mtime}

                # 서버로부터 완료 메시지 수신 대기
                response = client_socket.recv(1024).decode()
                if response == 'END':
                    print(f"서버측 파일 저장 완료. : {response}")
                    logging.info(f"서버측 파일 저장 완료. : {response}")
                else:
                    print(f"서버로부터 예상치 못한 메시지 수신: {response}")
                    logging.error(f"서버로부터 예상치 못한 메시지 수신: {response}")

                # 전송 후 checked_files 저장
                save_checked_files(checked_files)
                print(f"파일정보 저장완료 : checked_files.pkl\n")
                logging.error(f"파일정보 저장완료 : checked_files.pkl\n")
        except Exception as e:
            print(f"오류 발생 : {e}")
            logging.error(f"오류 발생 : {e}")
            exit()
        time.sleep(5)

    # 프로그램 종료 시 checked_files 저장
    save_checked_files(checked_files)
    client_socket.close()
    print("클라이언트 종료")
    logging.info("클라이언트 종료")
