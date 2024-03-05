import os
import tempfile
import pytest
import zipfile
from main import compress_object_to_zip

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
