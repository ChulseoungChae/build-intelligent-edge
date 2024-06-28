import boto3
import pandas as pd
import sys
import os
import io
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
    
    # 업로드할 로컬 경로 탐색
    file_list = []
    print('CSV 파일 목록 불러오는 중..')
    recursive_search_dir(src_local_path, file_list)
    
    # s3 client 선언
    s3_client = MinioData(upload_bucket_name)
    s3_client.set_client(service_name=service_name,
                            endpoint_url=endpoint_url,
                            aws_access_key_id=access_id,
                            aws_secret_access_key=access_key)

    # 버킷 존재 여부 확인
    buckets = s3_client.bucket_list()
    
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
            subpath = file_path.split('/')[-1]
            subpath = upload_path + '/' + subpath
            s3_client.upload(file_path, subpath, tags)
        print("Complete Upload file.")
    else:
        print(f"Bucket '{upload_bucket_name}' does not exist.")


if __name__ == "__main__":
    main()
