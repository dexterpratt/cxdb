# tests/test_utils.py

import pytest
import os
import tempfile
from cxdb.utils import load_config

@pytest.fixture
def temp_config_file():
    # Create a temporary config file for testing
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.ini') as temp_file:
        temp_file.write("""
[TestSection]
test_key = test_value
int_key = 42
float_key = 3.14

[AnotherSection]
another_key = another_value

[MixedCaseSection]
MixedCaseKey = mixed_case_value
""")
    yield temp_file.name
    os.unlink(temp_file.name)

def test_load_config_success(temp_config_file):
    value = load_config('TestSection', 'test_key', config_path=temp_config_file)
    assert value == 'test_value'

def test_load_config_int(temp_config_file):
    value = load_config('TestSection', 'int_key', config_path=temp_config_file)
    assert value == '42'  # Note: ConfigParser returns strings by default

def test_load_config_float(temp_config_file):
    value = load_config('TestSection', 'float_key', config_path=temp_config_file)
    assert value == '3.14'  # Note: ConfigParser returns strings by default

def test_load_config_fallback(temp_config_file):
    value = load_config('TestSection', 'non_existent_key', fallback='fallback_value', config_path=temp_config_file)
    assert value == 'fallback_value'

def test_load_config_missing_section(temp_config_file):
    with pytest.raises(ValueError, match="Key 'some_key' not found in section 'nonexistentsection' of the config file"):
        load_config('NonExistentSection', 'some_key', config_path=temp_config_file)

def test_load_config_missing_key(temp_config_file):
    with pytest.raises(ValueError, match="Key 'non_existent_key' not found in section 'testsection' of the config file"):
        load_config('TestSection', 'non_existent_key', config_path=temp_config_file)

def test_load_config_file_not_found():
    with pytest.raises(FileNotFoundError, match="Config file not found at"):
        load_config('TestSection', 'test_key', config_path='/path/to/non/existent/file.ini')

def test_load_config_different_section(temp_config_file):
    value = load_config('AnotherSection', 'another_key', config_path=temp_config_file)
    assert value == 'another_value'

def test_load_config_case_insensitive_section(temp_config_file):
    value = load_config('testsection', 'test_key', config_path=temp_config_file)
    assert value == 'test_value'

def test_load_config_case_insensitive_key(temp_config_file):
    value = load_config('TestSection', 'TEST_KEY', config_path=temp_config_file)
    assert value == 'test_value'

def test_load_config_mixed_case(temp_config_file):
    value = load_config('mixedcasesection', 'mixedcasekey', config_path=temp_config_file)
    assert value == 'mixed_case_value'