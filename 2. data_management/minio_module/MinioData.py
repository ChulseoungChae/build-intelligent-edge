import os
import io
import sys
import pandas as pd

import boto3 # pip install boto3


def printProgressBar(iteration, total, prefix = 'Progress', suffix = 'Complete',\
                      decimals = 1, length = 50, fill = '█'): 
    # 작업의 진행상황을 표시
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filledLength = int(length * iteration // total)
    bar = fill * filledLength + '-' * (length - filledLength)
    print('\r%s |%s| %s%% %s' %(prefix, bar, percent, suffix), end='\r')
    sys.stdout.flush()
    if iteration == total:
        print()


def remove_last_seperator(path):
    if path == "":
        pass
    elif path[-1] == "/" or path[-1] == "\\":
        path = path[:-1]
    return path


class MinioData(object):
    def __init__(self, bucket_name):
        self.bucket_name = bucket_name # 버킷 이름
        self.__service_name = ''
        self.__endpoint_url = ''
        self.__aws_access_key_id = ''
        self.__aws_secret_access_key = ''

        self.s3 = None
        self.s3_client = None


    # minio 연결
    def set_client(self, service_name, endpoint_url, aws_access_key_id, aws_secret_access_key):
        # 연결 정보 설정
        self.__service_name = service_name
        self.__endpoint_url = endpoint_url
        self.__aws_access_key_id = aws_access_key_id
        self.__aws_secret_access_key = aws_secret_access_key

        self.__connect() # minio 연결

        self.set_bucket(self.bucket_name)        
        
        if not self.isbucket(self.bucket_name): # 연결 정보의 버킷 존재 여부 확인
            exit(f"Bucket '{self.bucket_name}' does not exist.")

    
    # 버킷 설정
    def set_bucket(self, bucket_name):
        self.bucket = self.s3.Bucket(bucket_name)

        if self.bucket_name != bucket_name:
            self.bucket_name = bucket_name


    # minio 연결(직접 호출해서 사용 X, set_client()함수를 통해 사용)
    def __connect(self):
        try:
            self.s3 = boto3.resource(service_name='s3', 
                                    endpoint_url=self.__endpoint_url, #서버
                                    aws_access_key_id=self.__aws_access_key_id, # minio-web에서 생성한 접속 access-id
                                    aws_secret_access_key=self.__aws_secret_access_key) # minio-web에서 생성한 개인접속 access-key
            
            self.s3_client = boto3.client(service_name=self.__service_name, # 서비스 이름
                                    endpoint_url=self.__endpoint_url, #서버
                                    aws_access_key_id=self.__aws_access_key_id, # minio-web에서 생성한 접속 access-id
                                    aws_secret_access_key=self.__aws_secret_access_key) # minio-web에서 생성한 개인접속 access-key

            print(f"minIO Connected.")
        except Exception as err:
            raise Exception(err)
        
    
    # 버킷 조회
    def bucket_list(self):
        response = self.s3_client.list_buckets() # bucket 목록
        buckets = [bucket['Name'] for bucket in response['Buckets']]

        return buckets


    # 버킷 존재 여부 확인
    def isbucket(self, bucket_name):
        if bucket_name not in self.bucket_list():
            return False
        return True


    # 파일 조회
    def file_list(self, csv_path='', desired_extension=None):
        files = []

        for obj in self.bucket.objects.filter(Prefix = csv_path):        
            if desired_extension is None or obj.key.endswith(desired_extension.lower()) or obj.key.endswith(desired_extension.upper()):
                files.append(obj.key)

        if len(files) == 0:
            print(f'\'{self.bucket_name}\'bucket: \'{csv_path}\'path에 파일이 존재하지 않습니다.')
        
        return files

    # # tag list
    # def tag_list(self, csv_path=''):
    #     tag_list = []

    #     objects = list(self.bucket.objects.filter(Prefix = csv_path))

    #     for obj in objects:
    #         printProgressBar(objects.index(obj),len(objects), "Searching")
    #         tags = self.s3_client.get_object_tagging(Bucket=self.bucket_name, Key=obj.key)['TagSet']
    #         for tag in tags:
    #             tag_list.append(f"Tag Key: {tag['Key']}, Tag Value: {tag['Value']}")
        
    #     return tag_list


    # tag 파일 조회
    def file_list_with_tag(self, tag_key, tag_value, csv_path=''):
        files_with_tag = []
        objects = list(self.bucket.objects.filter(Prefix = csv_path))

        for obj in objects:
            printProgressBar(objects.index(obj),len(objects), "Searching")
            tags = self.s3_client.get_object_tagging(Bucket=self.bucket_name, Key=obj.key)['TagSet']
            if any(tag['Key'] == tag_key and tag['Value'] == tag_value for tag in tags):
                files_with_tag.append(obj.key)

        return files_with_tag


    # txt file read
    def read(self, file_path, decode='utf-8'):
        # file not save for disk
        obj = self.s3_client.get_object(Bucket=self.bucket_name, Key=file_path)

        file_content = obj["Body"].read().decode(decode)

        return file_content


    # csv -> df
    def csv_to_df(self, csv_path, **kwargs):
        # file not save for disk
        obj = self.s3_client.get_object(Bucket=self.bucket_name, Key=csv_path)

        if 'chunksize' not in kwargs:
            kwargs['chunksize'] = 50000

        df = pd.concat(pd.read_csv(io.BytesIO(obj["Body"].read()), **kwargs))

        return df
    

    # minio에 업로드
    def upload(self, src_local_path, remote_path, tags=None, part_size=10*1024*1024):
        src_local_path = os.path.abspath(src_local_path)

        if os.path.isdir(src_local_path): # dir
            src_local_path = remove_last_seperator(src_local_path)
            remote_path = remove_last_seperator(remote_path)

            for file in os.listdir(src_local_path):
                self.upload(src_local_path+'/'+file, remote_path+'/'+file)
        else: # file
            # multipart upload
            file = open(src_local_path, 'rb')
            self.multipart_upload(file, remote_path, tags, os.path.getsize(src_local_path), part_size)
            file.close()
            
            print(f"Upload Successful! {src_local_path} --> Bucket:'{self.bucket_name}' path:{remote_path}")


    # df의 데이터를 csv로 변환 후 minio에 업로드
    def df_upload(self, df, csv_path, encode='utf-8', tags=None, part_size=8*1024*1024, mode='a'):
        response = self.s3_client.list_objects_v2(Bucket=self.bucket_name, Prefix=csv_path, MaxKeys=1)

        if mode == 'a': # 이어쓰기 기능 (default)
            if 'Contents' in response:
                current_df = self.csv_to_df(csv_path, encoding=encode) # read current data from bucket as data frame
                df = pd.concat([current_df, df], ignore_index=True) # append data
        else:   # mode == 'w'
            pass

        csv_buf = io.BytesIO()
        df.to_csv(csv_buf,index=False,encoding=encode) # DataFrame -> CSV 변환/문자열 저장 -> 바이트 스트림으로 변환
        csv_buf.seek(0)

        # multipart upload
        self.multipart_upload(csv_buf, csv_path, tags, csv_buf.getbuffer().nbytes, part_size)

        print(f"Upload Successful! df --> Bucket:'{self.bucket_name}' path:{csv_path}")


    # 대용량 파일을 조각으로 분할하여 업로드(multipart upload=>대용량 처리)
    def multipart_upload(self, file, remote_path, tags, file_size, part_size):
        multipart_args = {
            'Bucket':self.bucket_name,
            'Key':remote_path
        }
        if os.path.splitext(remote_path)[1] == '.csv':
            multipart_args['ContentType'] = 'text/csv'
        if tags is not None:
            multipart_args['Tagging'] = ';'.join(['{}={}'.format(tag['Key'], tag['Value']) for tag in tags])

        response = self.s3_client.create_multipart_upload(**multipart_args)
        upload_id = response['UploadId']

        self.uploaded_bytes = 0
        uploaded_parts = []
        part_number = 1

        while True:
            data = file.read(part_size)
            if not data:
                break
            
            # 조각 업로드
            response = self.s3_client.upload_part(
                Bucket=self.bucket_name,
                Key=remote_path,
                PartNumber=part_number,
                UploadId=upload_id,
                Body=data
            )
            
            # 업로드된 조각 정보 저장
            uploaded_parts.append({'PartNumber': part_number, 'ETag': response['ETag']})
            part_number += 1
            self.callback(len(data), file_size)

        # 멀티파트 업로드 완료
        response = self.s3_client.complete_multipart_upload(
            Bucket=self.bucket_name,
            Key=remote_path,
            UploadId=upload_id,
            MultipartUpload={'Parts': uploaded_parts}
        )


    # minio 파일 다운로드
    def download(self, remote_path, target_local_path, desired_extension=None, part_size=8*1024*1024, max_concurrency=1):
        config = boto3.s3.transfer.TransferConfig(
            multipart_threshold=part_size,
            max_concurrency=max_concurrency
        )

        for file in self.file_list(remote_path, desired_extension):
            file_size = self.s3.Object(self.bucket_name, file).content_length
            local_path = remove_last_seperator(target_local_path)

            if os.path.isdir(target_local_path): # dir
                local_path = local_path + '/' + file

            if file_size > 0:
                self.uploaded_bytes = 0
                os.makedirs(os.path.dirname(local_path), exist_ok=True)
                self.bucket.download_file(file, local_path, Config=config, Callback=lambda bytes_transferred: self.callback(bytes_transferred, file_size))

                print(f"Download Successful! Bucket:'{self.bucket_name}' path:{file} --> {local_path}")


    # progressbar
    uploaded_bytes = 0
    def callback(self, bytes_transferred, file_size):
        self.uploaded_bytes += bytes_transferred
        printProgressBar(self.uploaded_bytes,file_size)