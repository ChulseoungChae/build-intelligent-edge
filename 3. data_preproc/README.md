# 3. data_preproc
- 데이터 클라우드를 활용한 데이터 전처리 방법
----

## 디렉토리 구조
```bash
├── README.md
├── minio_module/
│   └── MinioData.py # Minio 관련 모듈 정의  
```

## 📌 extract_field
- Minio에 저장된 CSV파일을 읽어와서 사용자가 선정한 필드의 칼럼 추출.
- 추출된 CSV를 다시 사용자가 지정한 Minio 경로에 저장.
### 입력인자
```python
# service_name: 서비스 이름 (ex.'s3','ec2')
# endpoint_url: 서버 정보
# aws_access_key_id: minio-web에서 생성한 접속 access-id
# aws_secret_access_key: minio-web에서 생성한 개인접속 access-key
# bucket_name : minio bucket 명
# src_path : 필드를 추출할 파일들의 minio 경로
# upload_path : 필드가 추출된 파일들을 업로드할 minio 경로
# tags : tags 정보
# field : 추출할 필드명('|'로 구분', index나 필드명 입력)
```


## 📌 split_by_id
- Minio에 저장된 CSV파일을 읽어와서 사용자가 선정한 필드의 값별로 로우(line) 분류.
- 분류된 CSV를 다시 사용자가 지정한 Minio 경로에 저장.
### 입력인자
```python
# service_name: 서비스 이름 (ex.'s3','ec2')
# endpoint_url: 서버 정보
# aws_access_key_id: minio-web에서 생성한 접속 access-id
# aws_secret_access_key: minio-web에서 생성한 개인접속 access-key
# bucket_name : minio bucket 명
# src_path : 필드를 추출할 파일들의 minio 경로
# upload_path : 필드가 추출된 파일들을 업로드할 minio 경로
# tags : tags 정보
# field : 분류 기준이 될 필드명
```

### 코드 사용 예시
```bash
$ git clone https://github.com/ChulseoungChae/build-intelligent-edge.git
$ cd build-intelligent-edge/3. data_preproc/
$ pip3 install -r requirements.txt

● extract_field
  - 터미널에서 vim으로 extract_field.ini 수정 
    $ vim extract_field/extract_field.ini
  - 디렉토리 이동 및 업로드코드 실행
    $ cd extract_field
    $ bash extract_field.sh

● split_by_id
  - 터미널에서 vim으로 split_by_id.ini 수정 
    $ vim split_by_id/split_by_id.ini
  - 디렉토리 이동 및 업로드코드 실행
    $ cd split_by_id
    $ bash split_by_id.sh

```