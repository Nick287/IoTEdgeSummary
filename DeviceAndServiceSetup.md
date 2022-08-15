#

## 1.1 Azure IoT Hub Device Provisioning Service (DPS)

When the customers to use IoT device will face such a challenge, manufacturing factory/production in Asia, and the The products that are produced be shipped to Europe or North America for sell, and we must hope that the products has good performance, so we hope these IoT devices can be connected to the physical distance nearest IoTHub When it's activated, or if someone is migrating from Europe to The Americas, we want to switch servers that are physically closest. Azure DPS can help us in a scenario.
So DPS can help your customers activate and initialize the device just like you bought a new phone out of the box.

However, more factors are considered from a technical side such as encryption authentication methods, protocols, Regions, Manufacturing step, Quotas and Limits. You can get more information [What is Azure IoT Hub Device Provisioning Service?](https://docs.microsoft.com/en-us/azure/iot-dps/about-iot-dps)

For example, IoTHub support multiple encryption methods

- [Quickstart: Provision a simulated symmetric key device](https://docs.microsoft.com/en-us/azure/iot-dps/quick-create-simulated-device-symm-key?pivots=programming-language-csharp)
- [Quickstart: Provision an X.509 certificate simulated device](https://docs.microsoft.com/en-us/azure/iot-dps/quick-create-simulated-device-x509?tabs=windows&pivots=programming-language-csharp)
- [Quickstart: Provision a simulated TPM device](https://docs.microsoft.com/en-us/azure/iot-dps/quick-create-simulated-device-tpm?pivots=programming-language-csharp)

The following diagram shows how a device connects to IoTHub through DPS step by step. Please refer to the [official documentation](https://docs.microsoft.com/en-us/azure/iot-dps/concepts-roles-operations) for details.

![image](/img/sequence-auto-provision-device-vs.png)

## 1.2 IoTHub and device provision

Some customers can use Azure Portal to create IoTHub directly to meet their requirements, but most customers have development environments, staging, and multiple production environments, which can be challenging to deploy and maintain consistency.
In real customer scenarios there are often have multiple Azure service in same or different resource groups, so keeping them consistent can be challenging as well. In order to this, Scripts can be used to deploy and configure these Azure resources to ensure consistency. Humans can easily make mistakes, but machines not. We can trust scripts (infrastructure as code).

The best way to deploy Azure resources and configure? ARM templates! [What are ARM templates?](https://docs.microsoft.com/en-us/azure/azure-resource-manager/templates/overview)

So the script allows us to quickly replicate the environment and configure the environment through parameters. It is also reliable when you want to delete or make changes to complex environments, then replicate. For example, the dev environment need deploys emulators, but the production environment does not.

Here's an example
[Deploy an Azure IoT Hub and a storage account using an ARM template](https://docs.microsoft.com/en-us/azure/iot-hub/horizontal-arm-route-messages)

In this example, we can see that IoTHub is not only deployed service its also configured such as deployment area, service level (basic or S1), and IoTHub is bound with storage account use to route messages.

Here various properties you need can be configured in the ARM template
[Microsoft.Devices IotHubs](https://docs.microsoft.com/en-us/azure/templates/microsoft.devices/iothubs?tabs=bicep)

![image](/img/iothub-info.png)

Some customers prefer to use cross-platform languages because they may still use services from other cloud platforms, so course we can support cross-platform script to deploy and configure the IoT Hub and devices. Such as Terraform. [What is Terraform ? an infrastructure as code software tool](https://learn.hashicorp.com/terraform)

- [Overview of Terraform on Azure - What is Terraform?](https://docs.microsoft.com/en-us/azure/developer/terraform/overview)
- [Configure Terraform in Azure Cloud Shell with Bash](https://docs.microsoft.com/en-us/azure/developer/terraform/get-started-cloud-shell-bash?tabs=bash)
- [Configure Terraform in Azure Cloud Shell with PowerShell](https://docs.microsoft.com/en-us/azure/developer/terraform/get-started-cloud-shell-powershell?tabs=bash)
- [Configure Terraform in Windows with Bash](https://docs.microsoft.com/en-us/azure/developer/terraform/get-started-windows-bash?tabs=bash)
- [Configure Terraform in Windows with PowerShell](https://docs.microsoft.com/en-us/azure/developer/terraform/get-started-windows-powershell?tabs=bash)

So you can use Three-party/ Cross-platform solution (Terraform) to deploy and configure IoTHub, for example the follow code defines variables to deploys azure service in a recourse group called example-resources recourse and specifies location = "West Europe". And an associated Azure storage account is also deployed.

Similar to the ARM template, you can also set the resource service level for deployment (account_tier= "Standard" and sku {name = "S1" capacity = "1"})

```javascript
resource "azurerm_resource_group" "example" {
  name     = "example-resources"
  location = "West Europe"
}

resource "azurerm_storage_account" "example" {
  name                     = "examplestorage"
  resource_group_name      = azurerm_resource_group.example.name
  location                 = azurerm_resource_group.example.location
  account_tier             = "Standard"
  account_replication_type = "LRS"
}

resource "azurerm_storage_container" "example" {
  name                  = "examplecontainer"
  storage_account_name  = azurerm_storage_account.example.name
  container_access_type = "private"
}

resource "azurerm_eventhub_namespace" "example" {
  name                = "example-namespace"
  resource_group_name = azurerm_resource_group.example.name
  location            = azurerm_resource_group.example.location
  sku                 = "Basic"
}

resource "azurerm_eventhub" "example" {
  name                = "example-eventhub"
  resource_group_name = azurerm_resource_group.example.name
  namespace_name      = azurerm_eventhub_namespace.example.name
  partition_count     = 2
  message_retention   = 1
}

resource "azurerm_eventhub_authorization_rule" "example" {
  resource_group_name = azurerm_resource_group.example.name
  namespace_name      = azurerm_eventhub_namespace.example.name
  eventhub_name       = azurerm_eventhub.example.name
  name                = "acctest"
  send                = true
}

resource "azurerm_iothub" "example" {
  name                = "Example-IoTHub"
  resource_group_name = azurerm_resource_group.example.name
  location            = azurerm_resource_group.example.location

  sku {
    name     = "S1"
    capacity = "1"
  }

  endpoint {
    type                       = "AzureIotHub.StorageContainer"
    connection_string          = azurerm_storage_account.example.primary_blob_connection_string
    name                       = "export"
    batch_frequency_in_seconds = 60
    max_chunk_size_in_bytes    = 10485760
    container_name             = azurerm_storage_container.example.name
    encoding                   = "Avro"
    file_name_format           = "{iothub}/{partition}_{YYYY}_{MM}_{DD}_{HH}_{mm}"
  }

  endpoint {
    type              = "AzureIotHub.EventHub"
    connection_string = azurerm_eventhub_authorization_rule.example.primary_connection_string
    name              = "export2"
  }

  route {
    name           = "export"
    source         = "DeviceMessages"
    condition      = "true"
    endpoint_names = ["export"]
    enabled        = true
  }

  route {
    name           = "export2"
    source         = "DeviceMessages"
    condition      = "true"
    endpoint_names = ["export2"]
    enabled        = true
  }

  enrichment {
    key            = "tenant"
    value          = "$twin.tags.Tenant"
    endpoint_names = ["export", "export2"]
  }

  cloud_to_device {
    max_delivery_count = 30
    default_ttl        = "PT1H"
    feedback {
      time_to_live       = "PT1H10M"
      max_delivery_count = 15
      lock_duration      = "PT30S"
    }
  }

  tags = {
    purpose = "testing"
  }
}
```

Alternatively, you can use Cloud-init to deploy a virtual machine to complete the deployment of an IoTEdge simulator and then test it.

Please refer to the full script [CSE CodeHub](https://dev.azure.com/CSECodeHub/435025%20-%20Telstra%20-%20MLOps%20for%20Smart%20Video%20Platform%20LVA/_git/435025%20-%20Telstra%20-%20IaC?path=/terraform&version=GBmain)

```javascript 
# Create Virtual IoT Edge Device

resource "azurerm_public_ip" "iot_edge" {
  name                = "${var.PREFIX}-${var.REGION}-pip-mokvm-${var.ENV}"
  resource_group_name = var.RESOURCE_GROUP
  location            = var.LOCATION
  allocation_method   = "Dynamic"
  domain_name_label   = "a-${var.PREFIX}-${var.REGION}-ite-mokvm-${var.ENV}"
}

resource "azurerm_network_security_group" "iot_edge" {
  name                = "${var.PREFIX}-${var.REGION}-nsg-mokvm-${var.ENV}"
  resource_group_name = var.RESOURCE_GROUP
  location            = var.LOCATION

  security_rule {
    name                       = "default-allow-22"
    priority                   = 1000
    access                     = "Allow"
    direction                  = "Inbound"
    protocol                   = "Tcp"
    destination_port_range     = "22"
    source_address_prefix      = "*"
    source_port_range          = "*"
    destination_address_prefix = "*"
  }
}

resource "azurerm_virtual_network" "iot_edge" {
  name                = "${var.PREFIX}-${var.REGION}-${var.ENV}-vnet22"
  resource_group_name = var.RESOURCE_GROUP
  location            = var.LOCATION
  address_space       = ["10.22.0.0/16"]

  subnet {
    name           = "${var.PREFIX}-${var.REGION}-${var.ENV}-vnet22-sn01"
    address_prefix = "10.22.1.0/24"
    security_group = azurerm_network_security_group.iot_edge.id
  }

}

resource "azurerm_network_interface" "iot_edge" {
  name                = "${var.PREFIX}-${var.REGION}-nic-mokvm-${var.ENV}"
  resource_group_name = var.RESOURCE_GROUP
  location            = var.LOCATION

  ip_configuration {
    name                          = "${var.PREFIX}-${var.REGION}-ipc-mokvm-${var.ENV}"
    private_ip_address_allocation = "Dynamic"
    public_ip_address_id          = azurerm_public_ip.iot_edge.id
    subnet_id                     = azurerm_virtual_network.iot_edge.subnet.*.id[0]
  }
}
resource "tls_private_key" "vm_ssh" {
  algorithm = "RSA"
  rsa_bits  = 4096
}

resource "local_file" "ssh" {
  content         = tls_private_key.vm_ssh.private_key_pem
  filename        = "../.ssh/id_rsa"
  file_permission = "600"
}

resource "azurerm_linux_virtual_machine" "iot_edge" {
  name                            = "${var.PREFIX}-${var.REGION}-avm-mokvm-${var.ENV}"
  resource_group_name             = var.RESOURCE_GROUP
  location                        = var.LOCATION
  admin_username                  = var.IOT_EDGE_VM_USERNAME
  disable_password_authentication = true
  admin_ssh_key {
    username   = var.IOT_EDGE_VM_USERNAME
    public_key = tls_private_key.vm_ssh.public_key_openssh
  }

  provision_vm_agent         = false
  allow_extension_operations = false
  size                       = "Standard_DS1_v2"
  network_interface_ids = [
    azurerm_network_interface.iot_edge.id
  ]
  custom_data = base64encode(replace(file("cloud-init.yaml"), "<REPLACE_WITH_CONNECTION_STRING>", shell_script.register_iot_edge_device.output["connectionString"]))

  source_image_reference {
    offer     = "UbuntuServer"
    publisher = "Canonical"
    sku       = "18.04-LTS"
    version   = "latest"
  }

  os_disk {
    caching              = "ReadWrite"
    storage_account_type = "Premium_LRS"
  }

  depends_on = [shell_script.register_iot_edge_device]
}

output "public_ssh" {
  value = "ssh -i ../.ssh/id_rsa ${var.IOT_EDGE_VM_USERNAME}@${azurerm_public_ip.iot_edge.fqdn}"
}
```

## 1.3 Setup The dev&test Environment

As you know IoT Edge module is based on container technology, of course we can continue to use container development environment when developing.
However, if we use edge-specific features, we need to set up the development environment such as message routing.

You can set up the development environment and debug locally. Please follow the documentation below to set it up environment.
[Use Visual Studio Code to develop and debug modules for Azure IoT Edge](https://docs.microsoft.com/en-us/azure/iot-edge/how-to-vs-code-develop-module?view=iotedge-2020-11)
[Tutorial: Develop IoT Edge modules with Linux containers.](https://docs.microsoft.com/en-us/azure/iot-edge/tutorial-develop-for-linux?view=iotedge-2020-11)

You can also consider the Dev Container environment, If you are familiar with containers this method may be more suitable for you.
[Developing inside a Container](https://code.visualstudio.com/docs/remote/containers)
![image](/img/architecture-containers.png)

[Dev Container start steps](https://github.com/Azure/iotedgedev/wiki/quickstart)

This dev container can give you as a full feature development environment you can take advantage of this.

- this dev container already wrapping all the dependencies in the component such iot edge dev tools, python, docker compose etc.
- secure development environment, you can run you code in the dev container that provides a secure dev environment that is not run on your local host.
