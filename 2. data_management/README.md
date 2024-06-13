# 2. data_management
- 데이터 클라우드를 활용한 데이터 업로드/다운로드 방법
----

## 디렉토리 구조
```bash
├── README.md
├── minio_module/
│   └── MinioData.py # Minio 관련 모듈 정의  
├── upload_files/
│   ├── minio_upload.py
│   ├── upload_info.ini
│   └── upload_run.sh
├── download_files/
│   ├── minio_download.py
│   ├── download_info.ini
│   └── download_run.sh
└── sample_data/
```

## 📌 MinioData 모듈
### [모듈 종류]
```python
__init__(bucket_name) # 초기화

# bucket_name: 버킷 이름
```

```python
set_client(service_name, endpoint_url, aws_access_key_id, aws_secret_access_key) # minio 연결

# service_name: 서비스 이름 (ex.'s3','ec2')
# endpoint_url: 서버 정보
# aws_access_key_id: minio-web에서 생성한 접속 access-id
# aws_secret_access_key: minio-web에서 생성한 개인접속 access-key
```

```python
set_bucket(bucket_name) # 버킷 설정

# bucket_name: 버킷 이름
```

```python
__connect() # minio 연결(Private-직접 호출해서 사용 X, set_client()함수를 통해 사용)
```

```python
bucket_list() # 버킷 조회(연결한 서버의 전체 버킷 이름 조회)
```

```python
isbucket(bucket_name) # 버킷 존재 여부 확인

# bucket_name: 버킷 이름
```

```python
file_list(csv_path, desired_extension=None) # csv_path 경로의 파일 조회

# csv_path: 파일 경로
# desired_extension: 확장자(ex.'.txt', '.csv')
```

```python
file_list_with_tag(tag_key, tag_value, csv_path='') # tag로 파일 리스트 조회

# tag_key: 태그의 키
# tag_value: 태그의 값
# csv_path: 파일 경로
```

```python
read(file_path, decode='utf-8') # 파일 불러오기

# file_path: 파일 경로
# decode: 디코딩 정보
```

```python
csv_to_df(csv_path, **kwargs) # csv파일 df로 변환

# csv_path: 파일 경로
# **kwargs: pd.read_csv()의 매개변수 모두 사용 가능(ex.sep='|',skiprows=[2],nrows=5)
```

```python
upload(source_local_path, remote_path, tags=None, part_size=10*1024*1024) # minio에 폴더 or 파일 업로드

# source_local_path: 로컬 파일 경로
# remote_path: minio 파일 경로
# tags: 태그 정보(ex.[{'Key': 'key1','Value': 'value1'},{'Key': 'key2','Value': 'value2'}])
# part_size: 조각 크기 (10MB:10*1024*1024)
```

```python
df_upload(df, csv_path, encode='utf-8', tags=None, part_size=8*1024*1024) # df의 데이터를 csv로 변환 후 minio에 업로드

# csv_path: 파일 경로
# encode: 인코딩 정보
# tags: 태그 정보(ex.[{'Key': 'key1','Value': 'value1'},{'Key': 'key2','Value': 'value2'}])
# part_size: 조각 크기 (10MB:10*1024*1024)
```

```python
multipart_upload(file, remote_path, tags, file_size, part_size) # 대용량 파일을 조각으로 분할하여 업로드(대용량 처리에 적합)

# file: 업로드할 파일
# remote_path: minio 파일 경로
# tags: 태그 정보(ex.[{'Key': 'key1','Value': 'value1'},{'Key': 'key2','Value': 'value2'}])
# file_size: 파일 크기
# part_size: 조각 크기 (10MB:10*1024*1024)
```

```python
download(remote_path, target_local_path, desired_extension=None, part_size=1*1024*1024, max_concurrency=1) # minio 파일 다운로드

# remote_path: minio 파일 경로
# target_local_path: 로컬 파일 경로
# desired_extension: 확장자(ex.'.txt', '.csv')
# part_size: 조각 크기(file_size>part_size  ==> 멀티파트 업로드 진행)
# max_concurrency: 업로드 중 동시에 진행되는 파트 수
```

```python
uploaded_bytes = 0
callback(bytes_transferred, file_size) # progressbar

# bytes_transferred: 현재까지 전송된 바이트 수
# file_size: 파일 크기
```

## 📌 사용 방법
**1. boto3 install**
```bash
pip install boto3
```

**2. MinioData 선언 및 연결**
```python
from minIO.MinioData import MinioData

minio = MinioData('버킷이름')
minio.set_client('서비스 이름', '서버', 'access key', 'secret key')
```

**3. MinioData 활용**
```python
# 파일 리스트 조회

# 파일 경로로 조회
files = minio.file_list('파일 경로')

# 태그로 조회
files = minio.file_list_with_tag('tag_key', 'tag_value', '파일 경로')
```

```python
# 파일 불러오기
file_content = minio.read('파일 경로', 'decode')
```

```python
# csv 파일, df로 불러오기
df = minio.csv_to_df('csv 경로', 'encoding')
```

```python
# minio에 업로드
minio.upload('로컬 파일 경로', 'minio 저장 경로')
```

```python
# df의 데이터를 csv로 변환 후 minio에 업로드
minio.df_upload(df, '저장 경로+파일이름.csv', 'encode', 'tags')
```

```python
# minio 파일 다운로드
minio.download('minio 경로', '로컬 저장 경로')
```

## 📌 사용 예시(Upload & Download)
```bash
$ git clone https://github.com/ChulseoungChae/build-intelligent-edge.git
$ cd build-intelligent-edge/2. data_management/
$ pip3 install -r requirements.txt

● Upload
  - 터미널에서 vim으로 upload_info.ini 수정 (업로드할 minio 경로 수정 및 업로드할 로컬 파일 경로 수정)
    $ vim upload_files/upload_info.ini
  - 디렉토리 이동 및 업로드코드 실행
    $ cd upload_files
    $ bash upload_run.sh

● Download
  - 터미널에서 vim으로 download_info.ini 수정 (업로드할 minio 경로 수정 및 업로드할 로컬 파일 경로 수정)
    $ vim download_files/download_info.ini
  - 디렉토리 이동 및 업로드코드 실행
    $ cd download_files
    $ bash download_run.sh
```