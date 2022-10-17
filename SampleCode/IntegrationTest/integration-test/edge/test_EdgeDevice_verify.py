import pytest
import time
from time import sleep
from azure.iot.hub import IoTHubRegistryManager
from azure.iot.hub.models import Twin, TwinProperties, QuerySpecification, QueryResult
from azure.iot.hub.protocol.operations.devices_operations import DevicesOperations

def get_ai_latest_filename(iothub_connection_str: str, device_id: str, module_id: str):
    iothub_registry_manager = IoTHubRegistryManager.from_connection_string(iothub_connection_str)
    module_twin = iothub_registry_manager.get_module_twin(device_id,module_id)
    reportedTwins = module_twin.properties.reported
    if "LatestAIModelFileName" in reportedTwins:
        return reportedTwins["LatestAIModelFileName"]
    else:
        return None

def test_edge_device(config_iot_device):
    iothub_connection_str = config_iot_device["IOTHUB_CONNECTION_STRING"]
    device_id = config_iot_device["EDGE_DEVICE_ID"]
    downloader_module_id = config_iot_device["EDGE_DOWNLOADER_MODULE_NAME"]
    spatial_analysis_module_id = config_iot_device["EDGE_SPATIAL_ANALYSIS_MODULE_NAME"]
    latest_ai_model_name = config_iot_device["LATEST_AI_MODEL_NAME"]
    waiting_time = config_iot_device["WATTING_TIME"]
    # wait for iot edge model download file and switch ai model
    time.sleep(int(waiting_time))
    file_name_form_downloader = get_ai_latest_filename(iothub_connection_str,device_id,downloader_module_id)

    print("#######")
    print("####### Target Edge Device Name is "+ config_iot_device["EDGE_DEVICE_ID"])
    print("####### New AI Model Name is "+ config_iot_device["LATEST_AI_MODEL_NAME"])

    assert latest_ai_model_name == file_name_form_downloader
    
    # when spatial_analysis implementation switch logic
    # file_name_spatial_analysis = get_ai_latest_filename(iothub_connection_str,device_id,spatial_analysis_module_id)
    # assert latest_ai_model_name == file_name_spatial_analysis
