import logging
import os
import json
import boto3
import zipfile
import filetype
from http import HTTPStatus

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    try:
        for record in event.get('Records', []):
            bucket_name = record['s3']['bucket']['name']
            object_key = record['s3']['object']['key']
            logging.info(f"New object '{object_key}' uploaded to bucket '{bucket_name}'")

            downloaded_file = download_from_s3(bucket_name, object_key)
            if downloaded_file is None:
                logging.error(f"Download Error: S3 Object '{object_key}' from '{bucket_name}'")
                continue

            file_type = filetype.guess(downloaded_file)
            if file_type is not None and file_type.mime == 'application/zip':
                logging.error(f"File Already In Compressed Format: S3 Object '{object_key}' from '{bucket_name}'")
                continue

            compressed_file = compress_object_to_zip(downloaded_file)
            if compressed_file is None:
                logging.error(f"Compression Error: S3 Object '{object_key}' from '{bucket_name}'")
                continue
            
            compressed_file_path, compressed_file_key = compressed_file
            upload_to_s3_status = upload_to_s3(compressed_file_path, bucket_name, compressed_file_key)
            if not upload_to_s3_status:
                logging.error(f"Upload Error: S3 Object '{compressed_file_key}' to '{bucket_name}'")
                continue

            delete_from_s3_status = delete_from_s3(bucket_name, object_key)
            if not delete_from_s3_status:
                logging.error(f"Delete Error: S3 Object '{object_key}' to '{bucket_name}'")
                continue
            
            logging.info(f"'{object_key}' from bucket '{bucket_name}' has been processed")

    except Exception as e:
        logging.error(e, exc_info=True)

    return {
        "statusCode": HTTPStatus.OK.value
    }

def download_from_s3(bucket_name, key):
    try:
        file_path = f"/tmp/{os.path.basename(key)}"
        s3 = boto3.client('s3')
        s3.download_file(bucket_name, key, file_path)
        logging.info(f"Downloaded '{key}' from '{bucket_name}'")
        return file_path
    
    except Exception as e:
        logging.error(f"An error occurred while downloading from S3 bucket: {bucket_name}: {e}")
        return None
    
def compress_object_to_zip(source_file):
    try:
        source_dir = os.path.dirname(source_file)
        file_name = os.path.basename(source_file)
        output_zip = os.path.join(source_dir, os.path.splitext(file_name)[0] + ".zip")

        with zipfile.ZipFile(output_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
            zipf.write(source_file, file_name)
        
        logging.info(f"file '{source_file}' compressed as '{output_zip}'")
        return output_zip, os.path.splitext(file_name)[0] + ".zip"
    
    except Exception as e:
        logging.error(f"Compression failed: {str(e)}")
        return None

def upload_to_s3(file_path, bucket_name, key):
    try:
        logging.info(f"Uploading '{key}' from '{file_path} to S3 Bucket: '{bucket_name}'")
        s3 = boto3.client('s3')
        s3.upload_file(file_path, bucket_name, key)
        logging.info("{file_path} uploaded successfully")
        return True
    except Exception as e:
        logging.error(f"Upload failed: {e}")
        return False

def delete_from_s3(bucket_name, key):
    try:
        logging.info(f"Deleting '{key}' from S3 Bucket: '{bucket_name}'")
        s3 = boto3.client('s3')
        s3.delete_object(Bucket=bucket_name, Key=key)
        logging.info(f"'{key}' deleted from '{bucket_name}' successfully")
        return True
    except Exception as e:
        logging.error(f"Deletion failed: {e}")
        return False