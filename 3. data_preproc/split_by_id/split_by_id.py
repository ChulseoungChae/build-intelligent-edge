import os
import pandas as pd
import sys
sys.path.append("../minio_module/")
from MinioData import MinioData


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


def main():
    if len(sys.argv) < 10:
        print('입력인자를 잘못 입력하였습니다. (총 9개)')
    print(sys.argv)
    service_name = sys.argv[1]
    endpoint_url = sys.argv[2]
    access_id = sys.argv[3]
    access_key = sys.argv[4]
    bucket_name = sys.argv[5]
    src_path = sys.argv[6]
    upload_path = sys.argv[7]
    tags = sys.argv[8]
    field = sys.argv[9]
        
    # s3 client 선언
    s3_client = MinioData(bucket_name)
    s3_client.set_client(service_name=service_name,
                            endpoint_url=endpoint_url,
                            aws_access_key_id=access_id,
                            aws_secret_access_key=access_key)
    
    # 태그 추가
    if tags == 'None':
        tags = None
    else:
        tags = None
        #tags = [{'Key': 'Type', 'Value': 'origin'}]
    
    file_listfile_list
    csv_list = s3_client.file_list(src_path)
    
    print("\nCSV 파일 리스트")
    print(csv_list)
    
    cnt = 1
    t_len = len(csv_list)
    df_list = []
    print("\n분류 시작")
    for csv_file in csv_list:
        printProgressBar(cnt, t_len)
        df = s3_client.csv_to_df(csv_file)
        for _id in list(df[field].unique()):
            new_df = df[df[field] == _id].copy()
            subpath = csv_file.split(src_path + '/')[-1]
            subpath = upload_path + '/' + subpath + '/' + str(_id)
            s3_client.df_upload(new_df, subpath)
        cnt += 1

    print("\n지정된 필드가 추출된 파일 업로드 경로 : " % upload_path)
    
    
if __name__ == "__main__":
    main()
