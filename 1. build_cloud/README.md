# 1. build_cloud
- 데이터 관리를 위한 클라우드 설치법
- 서비스를 시작하는 방법은 여러가지가 있지만, 본 문서에서는 독립 환경에서 실행하기 위해 docker를 사용해서 구축하는 방법을 소개함(docker 설치 필요)
----

## 특징
- AWS S3 같은 Object Storage 는 Data-Lake 의 용도로 활용됨
- MinIO는 단독 모드 (Stand-alone), 이레이저 코드 모드 (Erasure Code), 분산 모드 (Distributed)으로 설치 및 운영 가능
- 파이썬에서 boto, minio 등의 s3호환 라이브러리를 사용하여 코드에서 직접 파일에 접근가능
- 노드 연결을 통한 용량 확장 가능
- Kafka-Connect, Spark, Flink 와 같은 데이터 프로세싱 어플리케이션에 의해서 DataSource, DataSink 의 타겟으로 활용
- min.io는 (aws) S3와 호환되는 고성능의 오브젝트 스토리지. 즉, 스토리지 서비스를 구축하는데 사용할 수 있는 오픈 소스 솔루션 
- S3와 사용법이 거의 유사하게 되어 있어서, S3 사용경험이 있으면 매우 쉽게 사용이 가능
- 오브젝트 스토리지를 사용하고 있기 때문에 파일에 대한 직접적인 수정은 불가능하며, 항상 덮어쓰는 방식이 사용됨
- minio는 Docker / Mac / Linux / Windows / FreeBSD 환경에서 사용이 가능

## 사용법
- docker-compose.yml 파일을 아래와 같이 작성
```yaml
version: '3'
services:
  minio:
    image: quay.io/minio/minio:latest
    ports:
      - 9000:9000
      - 9001:9001
    environment:
      MINIO_ROOT_USER: admin
      MINIO_ROOT_PASSWORD: changeme
    volumes:
      - ./storage/minio:/data
    command: server /data --console-address ":9001"
```

- Docker 컨테이너 실행
```bash
$ docker-compose up -d
```

- 도커 컨테이너가 제대로 실행되어 돌아가면, 브라우저를 열어서 http://localhost:9000 으로 접속을 시도
- 요청은 http://localhost:9001로 redirect 되며, 아래와 같은 admin 페이지 로그인 창이 뜸
  - [login](./image/image-1693890781426.png)