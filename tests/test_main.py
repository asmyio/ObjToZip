import os
import tempfile
import pytest
import zipfile
from main import compress_object_to_zip, download_from_s3, upload_to_s3
from unittest.mock import Mock, patch

@pytest.fixture
def source_file():
    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        temp_file.write(b"Hello, this is a test file.")
        temp_file.flush()
        yield temp_file.name
        os.remove(temp_file.name)

def test_compress_object_to_zip(source_file):
    assert compress_object_to_zip(source_file) is True

    output_zip = os.path.splitext(source_file)[0] + ".zip"
    assert os.path.exists(output_zip)
    with zipfile.ZipFile(output_zip, 'r') as zipf:
        assert len(zipf.namelist()) == 1
        assert zipf.namelist()[0] == os.path.basename(source_file)

def test_compress_object_to_zip_failure():
    assert not compress_object_to_zip("nonexistent_file.txt")
    os.remove("nonexistent_file.zip")

@pytest.fixture
def s3_client_mock():
    with patch('boto3.client') as mock:
        yield mock

def test_download_from_s3(s3_client_mock):

    bucket_name = 'test-bucket'
    key = 'test-file.txt'
    expected_file_path = f"/tmp/{os.path.basename(key)}"

    s3_client_mock.return_value.download_file = Mock()
    file_path = download_from_s3(bucket_name, key)

    s3_client_mock.assert_called_once_with('s3')
    s3_client_mock.return_value.download_file.assert_called_once_with(bucket_name, key, expected_file_path)

    assert file_path == expected_file_path

def test_upload_to_s3_success(s3_client_mock):
    file_path = '/path/to/file.txt'
    bucket_name = 'test-bucket'
    key = 'test-file.txt'

    s3_client_mock.return_value.upload_file = Mock()

    result = upload_to_s3(file_path, bucket_name, key)

    s3_client_mock.assert_called_once_with('s3')
    s3_client_mock.return_value.upload_file.assert_called_once_with(file_path, bucket_name, key)
    assert result is True

def test_upload_to_s3_failure(s3_client_mock):
    file_path = '/path/to/file.txt'
    bucket_name = 'test-bucket'
    key = 'test-file.txt'

    s3_client_mock.return_value.upload_file = Mock(side_effect=Exception('Upload failed'))

    result = upload_to_s3(file_path, bucket_name, key)

    s3_client_mock.assert_called_once_with('s3')
    s3_client_mock.return_value.upload_file.assert_called_once_with(file_path, bucket_name, key)
    assert result is False
