import boto3
import pandas as pd
import sys
import os
import io
import time
from urllib import parse
sys.path.append("../minio_module/")
from MinioData import MinioData


def recursive_search_dir(_nowDir, _filelist):
    dir_list = []  # 현재 디렉토리의 서브디렉토리가 담길 list
    f_list = os.listdir(_nowDir)
    for fname in f_list:
        if fname == "checked_files" or fname == "result_files":  # 이미 전처리한 폴더는 통과
            continue
        if os.path.isdir(_nowDir + "/" + fname):
            dir_list.append(_nowDir + "/" + fname)
        elif os.path.isfile(_nowDir + "/" + fname):
            file_extension = os.path.splitext(fname)[1]
            _filelist.append(_nowDir + "/" + fname)

    for toDir in dir_list:
        recursive_search_dir(toDir, _filelist)


def main():
    if len(sys.argv) < 9:
        print('입력인자를 잘못 입력하였습니다. (총 8개)')
    print(sys.argv)
    service_name = sys.argv[1]
    endpoint_url = sys.argv[2]
    access_id = sys.argv[3]
    access_key = sys.argv[4]
    upload_bucket_name = sys.argv[5]
    upload_path = sys.argv[6]
    src_local_path = sys.argv[7]
    tags = sys.argv[8]
      
    # s3 client 선언
    s3_client = MinioData(upload_bucket_name)
    s3_client.set_client(service_name=service_name,
                            endpoint_url=endpoint_url,
                            aws_access_key_id=access_id,
                            aws_secret_access_key=access_key)

    # 버킷 존재 여부 확인
    buckets = s3_client.bucket_list()
    
    while True:
        try:
            # 업로드할 로컬 경로 탐색
            file_list = []
            print('CSV 파일 목록 불러오는 중..')
            recursive_search_dir(src_local_path, file_list)
            
            # 태그 추가
            if tags == 'None':
                tags = None
            else:
                tags = None
                #tags = [{'Key': 'Type', 'Value': 'origin'}]
            
            # minio 업로드
            if upload_bucket_name in buckets:
                print(f"Bucket '{upload_bucket_name}' exists.")
                for file_path in file_list:
                    
                    # Minio에서 사용할 경로 생성
                    relative_path = os.path.relpath(file_path, src_local_path)
                    minio_path = os.path.join(upload_path, relative_path).replace("\\", "/")  # 윈도우 경로 처리
                    print(minio_path)

                    # Minio에 파일이 이미 있는지 확인
                    if s3_client.file_exists(minio_path):
                        # local_md5 = s3_client.calculate_md5(file_path)
                        # remote_stat = s3_client.get_file_stat(file_path)
                        # remote_md5 = remote_stat['ETag'].strip('"') if remote_stat else None
                        
                        # print(local_md5, remote_md5)

                        if s3_client.compare_file_size(file_path, minio_path):
                            print(f"File '{minio_path}' is already up-to-date in the bucket. Skipping upload.")
                        else:
                            print(f"File '{minio_path}' has changed. Uploading new version.")
                            s3_client.upload(file_path, minio_path, tags)
                    else:
                        print(f"File '{minio_path}' does not exist in the bucket. Uploading.")
                        s3_client.upload(file_path, minio_path, tags)
                    
                print("Complete Upload file.")
            else:
                print(f"Bucket '{upload_bucket_name}' does not exist.")
            time.sleep(3600)  # 10분 대기 후 다시 시도
        except Exception as e:
            print(f"오류 발생: {e}")
            time.sleep(3600)  # 10분 대기 후 다시 시도
        
        
if __name__ == "__main__":
    main()