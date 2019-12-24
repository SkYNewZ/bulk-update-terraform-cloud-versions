import pytest
import requests_mock
import requests
import json
from src.main import validate_terraform_version, AVAILABLE_TERRAFORM_VERSIONS

WORKSPACE_NAME = "my_workspace"
ORG = "my_org"

### validate_terraform_version ###
def test_validate_terraform_version_invalid_version():
    assert not validate_terraform_version("0.15")


def test_validate_terraform_version_valid_version():
    # For each defined version
    for v in AVAILABLE_TERRAFORM_VERSIONS:
        assert validate_terraform_version(v)
    # for a specific version
    assert validate_terraform_version(check="0.11.14")
    assert validate_terraform_version(check="0.12.18")


def test_validate_terraform_version_malformed_version():
    assert not validate_terraform_version("0")
    assert not validate_terraform_version("a")
    with pytest.raises(TypeError):
        # Raise TypeError because 0 is not iterable
        assert not validate_terraform_version(0)


### validate_terraform_version ###
