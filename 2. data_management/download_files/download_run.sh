if [ -f 'download_info.ini' ]; then
    source download_info.ini
    echo ""
    echo "using information in the info.ini file"
    echo ""
    echo ">>=============================================================="
    echo "실행 관련 주요 정보(run.sh)"
    echo "입력 bucket : "$download_bucket_name
    echo "업로드할 minio 입력 경로  : "$download_path
    echo "입력할 로컬 파일 경로 : "$src_local_path
    echo "tags 정보 : "$tags
    echo "==============================================================<<"
    python3 minio_download.py $service_name $endpoint_url $access_id $access_key $download_bucket_name $download_path $src_local_path $tags
    echo " *** end script run for PYTHON *** "
    exit 0 #finish successfully
else
    echo " *** Please check upload_info.ini *** "
    echo " *** end script run for PYTHON *** "
fi