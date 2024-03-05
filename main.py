import os 
import zipfile

def s3_check():
    pass

def download_from_s3():
    pass
    
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