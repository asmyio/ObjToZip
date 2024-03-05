import logging
import os
import tempfile
import pytest
import zipfile
from main import compress_object_to_zip, download_from_s3, upload_to_s3, delete_from_s3, lambda_handler
from unittest.mock import Mock, patch, MagicMock
from http import HTTPStatus

@pytest.fixture
def sample_event():
    return {
        "Records": [
            {
                "s3": {
                    "bucket": {
                        "name": "test-bucket"
                    },
                    "object": {
                        "key": "test-file.txt"
                    }
                }
            }
        ]
    }

def test_lambda_handler_success(sample_event):
    with patch('main.logging') as mock_logging, \
         patch('main.download_from_s3') as mock_download, \
         patch('main.compress_object_to_zip') as mock_compress, \
         patch('main.upload_to_s3') as mock_upload, \
         patch('main.delete_from_s3') as mock_delete:

        mock_download.return_value = 'downloaded_file.txt'
        mock_compress.return_value = 'compressed_file.zip'
        mock_upload.return_value = True

        result = lambda_handler(sample_event, None)

        assert mock_logging.info.call_count == 1
        assert mock_logging.error.call_count == 0

        mock_download.assert_called_once_with('test-bucket', 'test-file.txt')
        mock_compress.assert_called_once_with('downloaded_file.txt')
        mock_upload.assert_called_once_with('compressed_file.zip', 'test-bucket', 'test-file.txt')
        mock_delete.assert_called_once_with('test-bucket', 'test-file.txt')

        assert result == {"statusCode": HTTPStatus.OK.value}

@pytest.fixture
def source_file():
    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        temp_file.write(b"Hello, this is a test file.")
        temp_file.flush()
        yield temp_file.name
        os.remove(temp_file.name)

def test_compress_object_to_zip_success():
    with patch('main.zipfile.ZipFile') as mock_zipfile:

        mock_zipfile.return_value.__enter__.return_value = MagicMock()
        mock_zipfile.return_value.__exit__.return_value = False

        output_zip = compress_object_to_zip('/tmp/test-file.txt')
        mock_zipfile.assert_called_once_with('/tmp/test-file.zip', 'w', zipfile.ZIP_DEFLATED)
        mock_zipfile.return_value.__enter__.return_value.write.assert_called_once_with('/tmp/test-file.txt', 'test-file.txt')

        assert output_zip == '/tmp/test-file.zip'

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

def test_delete_object_from_s3_success(s3_client_mock):
    bucket_name = 'test-bucket'
    key = 'test-file.txt'

    s3_client_mock.return_value.delete_object = Mock()
    result = delete_from_s3(bucket_name, key)

    s3_client_mock.assert_called_once_with('s3')
    s3_client_mock.return_value.delete_object.assert_called_once_with(Bucket=bucket_name, Key=key)
    assert result is True

def test_delete_object_from_s3_failure(s3_client_mock):
    bucket_name = 'test-bucket'
    key = 'test-file.txt'

    s3_client_mock.return_value.delete_object = Mock(side_effect=Exception('Deletion failed'))

    result = delete_from_s3(bucket_name, key)

    s3_client_mock.assert_called_once_with('s3')
    s3_client_mock.return_value.delete_object.assert_called_once_with(Bucket=bucket_name, Key=key)
    assert result is False