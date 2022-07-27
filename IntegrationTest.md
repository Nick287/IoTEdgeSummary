#

## Integration test

Integration testing is a routine work each project and that is frequently asked questions raised because IoT Edge systems are often complex and can be tested in different scenarios, so here are some suggestions.

### Design test cases with event or data driven message

In IoT scenarios, the edge device often can collect some information, such as temperature and humidity data, or some certain data is generated on the device side so we can detect this kind of data, so lets call it event detection, so we can set a threshold on the device side that will trigger an event and we can send an alert when the event triggered.

Or your device is producing a dataset, and these data contains a specific data structure, probably its JSON object data. these data will sent back to the cloud as streaming data or upload as dump file.

So the key here is that whether events or data set will return the information to the IoT Hub.

### Use IoT Edge feature to trigger and send back expect results

For the trigger Please imagine event data mentioned above, we can use the Edge function to dynamically change the threshold. When the temperature and humidity are above the threshold, an alarm is sent. So base on that we can change a lower the threshold number to trigger the alarm and then send the alarm back to IoTHub.

In case of dataset We can do a switch (Or what we call this a data simulator) that produces a mock Dataset that we add it into source data flows. For example, simulate a message package that is passed into Edge Module via a routing message.

As a trigger switch, you need to consider the C2D message

[__C2D (Cloud-to-device)__](https://docs.microsoft.com/en-us/azure/iot-hub/iot-hub-devguide-c2d-guidance)

[Direct methods](https://docs.microsoft.com/en-us/azure/iot-hub/iot-hub-devguide-direct-methods) for communications that require immediate confirmation of the result. Direct methods are often used for interactive control of devices such as turning on a fan.

[Twin's desired](https://docs.microsoft.com/en-us/azure/iot-hub/iot-hub-devguide-device-twins) properties for long-running commands intended to put the device into a certain desired state. For example, set the telemetry send interval to 30 minutes.

[Cloud-to-device](https://docs.microsoft.com/en-us/azure/iot-hub/iot-hub-devguide-messages-c2d) messages for one-way notifications to the device app.

When the expect data is generated we need to send it to IoTHub using D2C message, after that don't forget to clean up the test data when validation is complete.

[__D2C (Device-to-cloud)__](https://docs.microsoft.com/en-us/azure/iot-hub/iot-hub-devguide-d2c-guidance)

[Device-to-cloud](https://docs.microsoft.com/en-us/azure/iot-hub/iot-hub-devguide-messages-d2c) messages for time series telemetry and alerts.

[Device twin's reported properties](https://docs.microsoft.com/en-us/azure/iot-hub/iot-hub-devguide-device-twins) for reporting device state information such as available capabilities, conditions, or the state of long-running workflows. For example, configuration and software updates.

[File uploads](https://docs.microsoft.com/en-us/azure/iot-hub/iot-hub-devguide-file-upload) for media files and large telemetry batches uploaded by intermittently connected devices or compressed to save bandwidth.

### Verify the result by IoT hub synchronization data with Edge device

The verification process, I usually use the IoTHub SDK and leverage ADO Pipeline to run the verification script. I recommend [pytest](https://docs.pytest.org/en/7.1.x/getting-started.html) here because it is easy to integration with ADO [Shell Script task](https://docs.microsoft.com/en-us/azure/devops/pipelines/tasks/utility/shell-script?view=azure-devops) and its can generate test results as cover the page, and plus Python IoTHub SDK is easy to use. In particular, native debugging is also supported, and you don't want to debug your code in ADO, which can be a painful.

![image](/img/testresult.png)

### Sample code

Based on the above pattern, I have a more complex test example that has an AI model ready to deploy to the Edge Module keep in Blob Storage on cloud. I generated the SAS token of BLOb through a Web API and sent it to the Edge Module through Module Twin for download and verification.

![image](/img/AIdownload.png)

Sample code [ADO Pipeline](https://dev.azure.com/ganwa/SmartVideoMLOps/_git/smart-video-mlops?path=/devops/integration-test/05-integration-test.yml)

![image](/img/testpipeline.png)
