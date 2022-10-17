import pytest
import requests
 

def test_web_api(config_web_api):
    post_body = "{\"device\": \"%s\",\"name\": \"%s\"}" % (config_web_api["EDGE_DEVICE_ID"], config_web_api["LATEST_AI_MODEL_NAME"])
    post_headers = \
        {
            config_web_api["WEBAPI_HEADER_KEY"]: config_web_api["WEBAPI_HEADER_VALUE"]
        }
    resp = requests.post(config_web_api["WEBAPI_URL"],headers = post_headers, data = post_body)

    print("#######")
    print("####### Target Edge Device Name is "+ config_web_api["EDGE_DEVICE_ID"])
    print("####### New AI Model Name is "+ config_web_api["LATEST_AI_MODEL_NAME"])

    assert resp.status_code == 200