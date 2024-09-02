import socket
import os
import logging  # logging 모듈 임포트

# 로그 설정
logging.basicConfig(filename='log.txt', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

# 서버 설정
HOST = '0.0.0.0'
PORT = 5001


# 소켓 생성
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((HOST, PORT))
server_socket.listen(1)

print("\n서버가 시작되었습니다. 클라이언트를 기다리는 중입니다...")
logging.info("\n서버가 시작되었습니다. 클라이언트를 기다리는 중입니다...")

# 클라이언트 연결 수락
conn, addr = server_socket.accept()
print(f'{addr}가 연결되었습니다.')
logging.info(f'{addr}가 연결되었습니다.')
last_message=False
while True:
    try:
        # 파일 이름 수신
        if last_message and last_message.decode().startswith("FILENAME:"):
            file_name = last_message.decode().split(":", 1)[1]
            last_message = False
        else:
            file_name_message = conn.recv(1024).decode()
            if not file_name_message.startswith("FILENAME:"):
                print("파일 이름을 수신하지 못했습니다. 연결 종료.")
                logging.warning("파일 이름을 수신하지 못했습니다. 연결 종료.")
                break
            file_name = file_name_message.split(":", 1)[1]
        file_name = file_name.replace("\\", "/")
        print(f'파일명 {file_name}을(를) 수신함...')
        logging.info(f'파일명 {file_name}을(를) 수신함...')
        # 파일명 수신 확인 메시지 전송
        conn.sendall(b'READY')
        print('파일명 수신 확인 메시지 전송. 파일 내용 수신중..')
        logging.info('파일명 수신 확인 메시지 전송.  파일 내용 수신중..')
        
        # 파일 수신 및 저장
        dir_path = os.path.dirname(file_name)
        if not os.path.isdir(dir_path):
            os.makedirs(dir_path)
        with open(file_name, 'wb') as file:
            while True:
                data = conn.recv(4096)
                if b"EOF" in data: # "EOF"로 끝나면
                    file.write(data.split(b"EOF")[0]) 
                    last_message = data.split(b"EOF")[1]
                    if last_message == b'':
                        last_message = False
                    break
                file.write(data)

        print(f'{file_name} 파일을 저장했습니다.')
        logging.info(f'{file_name} 파일을 저장했습니다.')
        # 파일 수신이 완료되면 클라이언트에게 완료 메시지 전송
        conn.sendall(b'END')
        print("클라이언트에게 완료 메시지 전송\n")
        logging.info("클라이언트에게 완료 메시지 전송\n")

        
    except Exception as e:
        print(f"파일 수신 중 오류 발생: {e}")
        logging.error(f"파일 수신 중 오류 발생: {e}")
        break

# 연결 종료
conn.close()
server_socket.close()

print("서버 종료")
logging.info("서버 종료")