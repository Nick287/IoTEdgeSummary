# Configure the Azure provider
terraform {
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 2.65"
    }
    shell = {
      source  = "scottwinkler/shell"
      version = "1.7.7"
    }
  }

  required_version = ">= 0.14.9"
}

provider "azurerm" {
  features {}
}

data "azurerm_subscription" "current" {
}

data "azurerm_client_config" "current" {
}

output "current_subscription_display_name" {
  value = data.azurerm_subscription.current.subscription_id
}


# Test azurerm_role_assignment
output "current_sp_display_name" {
  value = data.azurerm_client_config.current.client_id
}

data "azurerm_resources" "example" {
  resource_group_name = "garyhome"
}

resource "azurerm_role_assignment" "example" {
  scope                = data.azurerm_subscription.current.id
  # scope                = data.azurerm_resources.example.id
  role_definition_name = "Reader"
  principal_id         = data.azurerm_client_config.current.object_id
}

locals {
  dns_label_prefix = "garyh"
  location = "eastasia"
  resource_group_name = "garyhome"
  vm_user_name = "gary"
}

# Deploy IoT Edge Modules
# resource "shell_script" "deploy_iot_edge_modules" {
#   lifecycle_commands {
#     create = "$script create"
#     read   = "$script read"
#     delete = "$script delete"
#   }

#   working_directory = "../../../scripts/terraform/"
#   environment = {
#     resource_group_name="sv0dd0d8f4-rg"
#     ava_name="sv0dd0d8f4ava"
#     ava_edgemodule_name="sv0dd0d8f4edgemodule"
#     iot_hub_name="sv0dd0d8f4-iot-hub"
#     iot_edge_device_name="sv0dd0d8f4-edge-device"
#     script               = "./deploy_iot_edge_modules.sh"
#   }
# }

### Create Virtual IoT Edge Device ###

/* resource "azurerm_public_ip" "iot_edge" {
  name                = "${local.dns_label_prefix}-ip"
  resource_group_name = local.resource_group_name
  location            = local.location
  allocation_method   = "Dynamic"
  domain_name_label   = "a-${local.dns_label_prefix}"
}

resource "azurerm_network_security_group" "iot_edge" {
  name                = "${local.dns_label_prefix}-nsg"
  resource_group_name = local.resource_group_name
  location            = local.location

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
  name                = "${local.dns_label_prefix}-vnet"
  location            = local.location
  resource_group_name = local.resource_group_name
  address_space       = ["10.0.0.0/16"]

  subnet {
    name           = "${local.dns_label_prefix}-subnet"
    address_prefix = "10.0.1.0/24"
    security_group = azurerm_network_security_group.iot_edge.id
  }

}

resource "azurerm_network_interface" "iot_edge" {
  name                = "${local.dns_label_prefix}-nic"
  location            = local.location
  resource_group_name = local.resource_group_name

  ip_configuration {
    name                          = "${local.dns_label_prefix}-ipconfig"
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
  name                            = "${local.dns_label_prefix}-vm"
  location                        = local.location
  resource_group_name             = local.resource_group_name
  admin_username                  = local.vm_user_name
  disable_password_authentication = true
  admin_ssh_key {
    username   = local.vm_user_name
    public_key = tls_private_key.vm_ssh.public_key_openssh
  }

  provision_vm_agent         = false
  allow_extension_operations = false
  size                       = "Standard_DS1_v2"
  network_interface_ids = [
    azurerm_network_interface.iot_edge.id
  ]
  # custom_data = base64encode(replace(file("${path.module}/cloud-init.yaml"), "<REPLACE_WITH_CONNECTION_STRING>", var.edge_device_connection_string))

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
}

output "public_ssh" {
  value = "ssh -i ../.ssh/id_rsa ${local.vm_user_name}@${azurerm_public_ip.iot_edge.fqdn}"
} */