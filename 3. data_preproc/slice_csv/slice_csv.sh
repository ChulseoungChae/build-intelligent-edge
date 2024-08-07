if [ -f 'upload_info.ini' ]; then
    source upload_info.ini
    echo ""
    echo "using information in the info.ini file"
    echo ""
    echo ">>=============================================================="
    echo "실행 관련 주요 정보(run.sh)"
    echo "입력 bucket : "$bucket_name
    echo "분류할 파일들의 minio 경로  : "$src_path
    echo "분류된 파일들을 업로드할 minio 경로 : "$upload_path
    echo "tags 정보 : "$tags
    echo "분리 기준이 될 CSV라인수 : "$slice_size
    echo "==============================================================<<"
    python3 minio_upload.py $service_name $endpoint_url $access_id $access_key $bucket_name $src_path $upload_path $tags $slice_size
    echo " *** end script run for PYTHON *** "
    exit 0 #finish successfully
else
    echo " *** Please check upload_info.ini *** "
    echo " *** end script run for PYTHON *** "
fi