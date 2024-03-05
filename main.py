import os
import boto3
import zipfile

def s3_check():
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

def upload_to_s3():
    pass 

def delete_object_from_s3():
    pass 

def main(): 
    pass 

if __name__ == "__main__":
    main()