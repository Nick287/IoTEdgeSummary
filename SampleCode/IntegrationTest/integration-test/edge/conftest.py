"""Test fixtures"""
import os
import pytest

# test_iothub_connection_str = "HostName=avasamplewic5tgxmz3mvq.azure-devices.net;SharedAccessKeyName=iothubowner;SharedAccessKey=DgvuSook93iOjvxffYmD67GrEy9iXOTczxJN+gZvesM="
# test_device_id = "avasample-iot-edge-device"

test_iothub_connection_str = "HostName=smvi-ae-ith-iothb-ssdev.azure-devices.net;SharedAccessKeyName=iothubowner;SharedAccessKey=fdFTbivMfNekd83o2F2woXCDRsBoQExnS4p1oNC4PCc="
test_device_id = "smvi-ae-avm-mokvm-ssdev-2"

downloader_module_id = "DownloaderModule"
spatial_analysis_module_id = "spatialAnalysis"
latest_ai_model_file_name = "tiny-yolov4-416-chatswood-entrance-camera_best_7.zip"
api_url = "https://sv-ae-fun-wbapi-ssdev.azurewebsites.net/api/MLModelSwitchingTrigger"
aip_key ="Ocp-Apim-Subscription-Key"
api_value="e0105a6eb95c43868bf60ceb57dd15b5"
waiting_time = 2

@pytest.fixture(scope="session")
def config_web_api():
    return {
        "EDGE_DEVICE_ID": os.getenv("EDGE_DEVICE_ID", test_device_id),
        "LATEST_AI_MODEL_NAME": os.getenv("LATEST_AI_MODEL_NAME", latest_ai_model_file_name),
        "WEBAPI_URL": os.getenv("WEBAPI_URL", api_url),
        "WEBAPI_HEADER_KEY": os.getenv("WEBAPI_HEADER_KEY", aip_key),
        "WEBAPI_HEADER_VALUE": os.getenv("WEBAPI_HEADER_VALUE", api_value)
    }

@pytest.fixture(scope="session")
def config_iot_device():
    return {
        "IOTHUB_CONNECTION_STRING": os.getenv("IOTHUB_CONNECTION_STRING",test_iothub_connection_str),
        "EDGE_DEVICE_ID": os.getenv("EDGE_DEVICE_ID",test_device_id),
        "EDGE_DOWNLOADER_MODULE_NAME": os.getenv("EDGE_DOWNLOADER_MODULE_NAME", downloader_module_id),
        "LATEST_AI_MODEL_NAME": os.getenv("LATEST_AI_MODEL_NAME", latest_ai_model_file_name),
        "EDGE_SPATIAL_ANALYSIS_MODULE_NAME": os.getenv("EDGE_SPATIAL_ANALYSIS_MODULE_NAME", spatial_analysis_module_id),
        "WATTING_TIME": os.getenv("WATTING_TIME", waiting_time)
    }

@pytest.fixture(scope="session")
def config_iot_ava_device():
    return {
        "IOTHUB_EVENTHUB_CONNECTION_STRING": os.getenv("IOTHUB_EVENTHUB_CONNECTION_STRING",test_iothub_connection_str),
        "EDGE_DEVICE_ID": os.getenv("EDGE_DEVICE_ID",test_device_id)
    }