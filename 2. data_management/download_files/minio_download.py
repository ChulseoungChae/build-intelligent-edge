import boto3
import pandas as pd
import sys
import os
import io
sys.path.append("../minio_module/")
from MinioData import MinioData

def main():
    service_name = sys.argv[1]
    endpoint_url = sys.argv[2]
    access_id = sys.argv[3]
    access_key = sys.argv[4]
    download_bucket_name = sys.argv[5]
    download_path = sys.argv[6]
    src_local_path = sys.argv[7]
    tags = sys.argv[8]
    
    # s3 client 선언
    s3_client = MinioData(download_bucket_name)
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

    if download_bucket_name in buckets:
        print(f"Bucket '{download_bucket_name}' exists.")
        s3_client.download(download_path, src_local_path)
        print("Complete Download file.")
    else:
        print(f"Bucket '{download_bucket_name}' does not exist.")


if __name__ == "__main__":
    main()
