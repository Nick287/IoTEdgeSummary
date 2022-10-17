import base64
import pytest
from azure.storage.blob import BlobServiceClient


def test_uploaded_model(blob_storage_config):
    storage_account_name = blob_storage_config["STORAGE_ACCOUNT_NAME"]
    storage_account_key = blob_storage_config["STORAGE_ACCOUNT_KEY"]
    storage_account_container = blob_storage_config["STORAGE_ACCOUNT_CONTAINER"]
    uploaded_model_name = blob_storage_config["UPLOADED_MODEL_NAME"]
    uploaded_model_zip_contents_md5 = blob_storage_config["UPLOADED_MODEL_ZIP_CONTENTS_MD5"]

    service_client = BlobServiceClient(
        account_url=f"https://{storage_account_name}.blob.core.windows.net",
        credential=storage_account_key
    )

    # Check existence of model zip file
    blob_client = service_client.get_blob_client(storage_account_container, uploaded_model_name)
    assert blob_client.exists() == True

    # Check contents MD5 of uploaded zip file
    blob_properties = blob_client.get_blob_properties()
    md5_bytearray = blob_properties.content_settings.content_md5
    md5_base64_bytes = base64.b64encode(md5_bytearray)
    md5_string = md5_base64_bytes.decode()
    assert md5_string == uploaded_model_zip_contents_md5

    # Check existence of model metadata json file
    blob_client = service_client.get_blob_client(storage_account_container, f"metadata_{uploaded_model_name.replace('.zip', '.json')}")
    assert blob_client.exists() == True

    blob_client.close()
    service_client.close()
