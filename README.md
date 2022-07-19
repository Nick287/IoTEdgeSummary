# Azure IoT Edge Manufacturing experience summary

## about this document

You're talking with customer about manufacturing or industrial scenarios and smart devices. But smart devices, smart factories, lots of interesting scenarios come to mind, and you're curious how do you implement those scenarios with Azure IoT/Edge?

This article will help you understand Azure IoT Edge's capabilities from different points.

1. Device and service setup
   1. Azure IoT Hub Device Provisioning Service (DPS)
   2. IoTHub Provisioning ARM template and Three-party/ Cross-platform solution (Terraform)
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

### 1.1 Azure IoT Hub Device Provisioning Service (DPS)

When the customers to use IoT device will face such a challenge, manufacturing factory/production in Asia, and the The products that are produced be shipped to Europe or North America for sell, and we must hope that the products has good performance, so we hope these IoT devices can be connected to the physical distance nearest IoTHub When it's activated, or if someone is migrating from Europe to The Americas, we want to switch servers that are physically closest. Azure DPS can help us in a scenario.
So DPS can help your customers activate and initialize the device just like you bought a new phone out of the box.

However, more factors are considered from a technical side such as encryption authentication methods, protocols, Regions, Manufacturing step, Quotas and Limits. You can get more information [What is Azure IoT Hub Device Provisioning Service?](https://docs.microsoft.com/en-us/azure/iot-dps/about-iot-dps)

For example, IoTHub support multiple encryption methods

- [Quickstart: Provision a simulated symmetric key device](https://docs.microsoft.com/en-us/azure/iot-dps/quick-create-simulated-device-symm-key?pivots=programming-language-csharp)
- [Quickstart: Provision an X.509 certificate simulated device](https://docs.microsoft.com/en-us/azure/iot-dps/quick-create-simulated-device-x509?tabs=windows&pivots=programming-language-csharp)
- [Quickstart: Provision a simulated TPM device](https://docs.microsoft.com/en-us/azure/iot-dps/quick-create-simulated-device-tpm?pivots=programming-language-csharp)

The following diagram shows how a device connects to IoTHub through DPS step by step. Please refer to the [official documentation](https://docs.microsoft.com/en-us/azure/iot-dps/concepts-roles-operations) for details.

![image](/img/sequence-auto-provision-device-vs.png)

<img src="/img/sequence-auto-provision-device-vs.png" width = "400" height = "300" />

### 1.2 IoTHub and device provision

Some customers can use Azure Portal to create IoTHub directly to meet their requirements, but most customers have development environments, staging, and multiple production environments, which can be challenging to deploy and maintain consistency.
In real customer scenarios there are often have multiple Azure service in same or different resource groups, so keeping them consistent can be challenging as well. In order to this, Scripts can be used to deploy and configure these Azure resources to ensure consistency. Humans can easily make mistakes, but machines not. We can trust scripts (infrastructure as code).

The best way to deploy Azure resources and configure? ARM templates! [What are ARM templates?](https://docs.microsoft.com/en-us/azure/azure-resource-manager/templates/overview)

So the script allows us to quickly replicate the environment and configure the environment through parameters. It is also reliable when you want to delete or make changes to complex environments, then replicate. For example, the dev environment need deploys emulators, but the production environment does not.

Here's an example
[Deploy an Azure IoT Hub and a storage account using an ARM template](https://docs.microsoft.com/en-us/azure/iot-hub/horizontal-arm-route-messages)

In this example, we can see that IoTHub is not only deployed service its also configured such as deployment area, service level (basic or S1), and IoTHub is bound with storage account use to route messages.

Here various properties you need can be configured in the ARM template
[Microsoft.Devices IotHubs](https://docs.microsoft.com/en-us/azure/templates/microsoft.devices/iothubs?tabs=bicep)

![image](/img/iothub-info.png =100x100)

Some customers prefer to use cross-platform languages because they may still use services from other cloud platforms, so course we can support cross-platform script to deploy and configure the IoT Hub and devices. Such as Terraform. [What is Terraform ? an infrastructure as code software tool](https://learn.hashicorp.com/terraform)

设备 与部署 连接  DPS
或者 是 部署 IoT hub 虚机
test terraform

AI enable
TensorFlow enable
ONNX
AVA pipeline

本地存储
module 之间分享数据
云之前同步数据  blob sync
SQL server

devops

部署设备
生成 deploy file  
package image
如何处理多个 image 并行处理
版本号 tag

集成测试
