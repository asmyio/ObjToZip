import os
import boto3
import zipfile

def lambda_handler(event, context):
    pass

def download_from_s3(bucket_name, key):
    try:
        file_path = f"/tmp/{os.path.basename(key)}"
        s3 = boto3.client('s3')
        s3.download_file(bucket_name, key, file_path)
        return file_path
    
    except Exception as e:
        print(f"An error occurred while downloading from S3 bucket: {bucket_name}: {e}")
        return None
    
def compress_object_to_zip(source_file):
    try:
        source_dir = os.path.dirname(source_file)
        file_name = os.path.basename(source_file)
        output_zip = os.path.join(source_dir, os.path.splitext(file_name)[0] + ".zip")

        with zipfile.ZipFile(output_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
            zipf.write(source_file, file_name)
        return True
    
    except Exception as e:
        print(f"Compression failed: {str(e)}")
        return False

def upload_to_s3(file_path, bucket_name, key):
    try:
        s3 = boto3.client('s3')
        s3.upload_file(file_path, bucket_name, key)
        print("Upload successful")
        return True
    except Exception as e:
        print(f"Upload failed: {e}")
        return False

def delete_from_s3(bucket_name, key):
    try:
        s3 = boto3.client('s3')
        s3.delete_object(Bucket=bucket_name, Key=key)
        print("Object deleted successfully")
        return True
    except Exception as e:
        print(f"Deletion failed: {e}")
        return False