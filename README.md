# Azure IoT Edge Manufacturing experience summary

## about this document

You're talking with customer about manufacturing or industrial scenarios and smart devices. But smart devices, smart factories, lots of interesting scenarios come to mind, and you're curious how do you implement those scenarios with Azure IoT/Edge?

This article will help you understand Azure IoT Edge's capabilities from different points.

1. [Device and service setup](/DeviceAndServiceSetup.md)
   1. [Azure IoT Hub Device Provisioning Service (DPS)](/DeviceAndServiceSetup.md#11-azure-iot-hub-device-provisioning-service-dps)
   2. [IoTHub Provisioning ARM template and Three-party/ Cross-platform solution (Terraform)](/DeviceAndServiceSetup.md#12-iothub-and-device-provision)
   3. Quickly setup the dev&test environment
2. Data storage and exchange
   1. Local storage - IO
   2. Share file/Data between Edge module
   3. Local database SQL server
   4. Sync data between cloud and Edge device
3. AI (Artificial intelligence) capabilities
   1. TensorFlow model enable on Edge device
   2. Cross-platform solution ONNX (Open Neural Network Exchange)
   3. Video streaming
4. Devops
   1. Package of multiple images(Multiple development languages) and upload to container registry (Parallel processing)
   2. Image version control
   3. Deployment file for Edge device
5. Integration testing
   1. Integrated test pattern
   2. Code sample
