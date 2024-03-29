# Azure IoT Edge Common Industrial Scenarios

## about this document

You're talking with customer about manufacturing or industrial scenarios and smart devices. But smart devices, smart factories, lots of interesting scenarios come to mind, and you're curious how do you implement those scenarios with Azure IoT/Edge?

This article will help you understand Azure IoT Edge's capabilities from different points.

1. [Device and service setup](/DeviceAndServiceSetup.md)
   1. [Azure IoT Hub Device Provisioning Service (DPS)](/DeviceAndServiceSetup.md#11-azure-iot-hub-device-provisioning-service-dps)
   2. [IoTHub Provisioning ARM template and Three-party/ Cross-platform solution (Terraform)](/DeviceAndServiceSetup.md#12-iothub-and-device-provision)
   3. [Quickly setup the dev&test environment](/DeviceAndServiceSetup.md#13-setup-the-devtest-environment)
2. [Data storage and exchange](/DataStorageAndExchange.md)
   1. [Local storage - IO](/DataStorageAndExchange.md#21-local-storage---io)
   2. [Share file/data between Edge module](/DataStorageAndExchange.md#22-share-filedata-between-edge-module)
   3. [Local database SQL server](/DataStorageAndExchange.md#23-local-database-sql-server)
   4. [Sync data between cloud and Edge device](/DataStorageAndExchange.md#24-sync-data-between-cloud-and-edge-device)
3. [AI (Artificial intelligence) capabilities](AIcapabilities.md)
   1. [TensorFlow model enable on Edge device](/AIcapabilities.md#tensorflow-model-enable-on-edge-device)
   2. [Cross-platform solution ONNX (Open Neural Network Exchange)](/AIcapabilities.md#open-neural-network-exchange-onnx)
4. [Devops](/EdgeDevops.md)
   1. [Package of multiple images(Multiple development languages) and upload to container registry (Parallel processing)](/EdgeDevops.md#package-images-and-upload-to-container-registry)
   2. [Image version control](/EdgeDevops.md#imagetag-used-for-version-control)
   3. [Deployment file for Edge device](/EdgeDevops.md#edge-module-image-deployment)
5. [Integration test](/IntegrationTest.md)
   1. [Integrated test pattern](/IntegrationTest.md#integration-test)
   2. [Sample code](/IntegrationTest.md#verify-the-result-by-iot-hub-synchronization-data-with-edge-device)
