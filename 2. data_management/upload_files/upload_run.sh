if [ -f 'upload_info.ini' ]; then
    source upload_info.ini
    echo ""
    echo "using information in the info.ini file"
    echo ""
    echo ">>=============================================================="
    echo "실행 관련 주요 정보(run.sh)"
    echo "입력 bucket : "$upload_bucket_name
    echo "업로드할 minio 입력 경로  : "$upload_path
    echo "입력할 로컬 파일 경로 : "$src_local_path
    echo "tags 정보 : "$tags
    echo "==============================================================<<"
    python3 minio_upload.py $service_name $endpoint_url $access_id $access_key $upload_bucket_name $upload_path $src_local_path $tags
    echo " *** end script run for PYTHON *** "
    exit 0 #finish successfully
else
    echo " *** Please check upload_info.ini *** "
    echo " *** end script run for PYTHON *** "
fi