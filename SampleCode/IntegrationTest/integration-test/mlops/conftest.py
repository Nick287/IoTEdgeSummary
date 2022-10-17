"""Test fixtures"""
import os
import pytest


@pytest.fixture(scope="session")
def blob_storage_config():
    return {
        "STORAGE_ACCOUNT_NAME": os.getenv("STORAGE_ACCOUNT_NAME"),
        "STORAGE_ACCOUNT_KEY": os.getenv("STORAGE_ACCOUNT_KEY"),
        "STORAGE_ACCOUNT_CONTAINER": os.getenv("STORAGE_ACCOUNT_CONTAINER", "amlmodels"),
        "UPLOADED_MODEL_NAME": os.getenv("UPLOADED_MODEL_NAME"),
        "UPLOADED_MODEL_ZIP_CONTENTS_MD5": os.getenv("UPLOADED_MODEL_ZIP_CONTENTS_MD5")
    }
