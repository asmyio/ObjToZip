import logging
import os
import tempfile
import pytest
import zipfile
from main import compress_object_to_zip, download_from_s3, upload_to_s3, delete_from_s3, lambda_handler
from unittest.mock import Mock, patch
from http import HTTPStatus

@patch('main.logging')
def test_lambda_handler_with_records(mock_logging):
    mock_event = {
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

    response = lambda_handler(mock_event, None)
    mock_logging.info.assert_called_once_with("new object 'test-file.txt' uploaded to bucket 'test-bucket'")

    assert response == {"statusCode": HTTPStatus.OK.value}

@patch('main.logging')
def test_lambda_handler_without_records(mock_logging):
    mock_event = {}
    response = lambda_handler(mock_event, None)
    mock_logging.error.assert_called()

    assert response == {"statusCode": HTTPStatus.OK.value}

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