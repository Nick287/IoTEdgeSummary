resource "azurerm_storage_account" "ava" {
  name                     = "${var.resource_prefix}avasa"
  resource_group_name      = var.resource_group_name
  location                 = var.video_analyzer_location
  account_tier             = "Standard"
  account_replication_type = "LRS"
}


resource "azurerm_user_assigned_identity" "sv" {
  name                = "${var.resource_prefix}assignedidentity"
  resource_group_name = var.resource_group_name
  location            = azurerm_storage_account.ava.location
}


resource "azurerm_role_assignment" "contributor" {
  scope                = azurerm_storage_account.ava.id
  role_definition_name = "Storage Blob Data Contributor"
  principal_id         = azurerm_user_assigned_identity.sv.principal_id
}

resource "azurerm_role_assignment" "reader" {
  scope                = azurerm_storage_account.ava.id
  role_definition_name = "Reader"
  principal_id         = azurerm_user_assigned_identity.sv.principal_id
}


resource "azurerm_video_analyzer" "sv" {
  name                = "${var.resource_prefix}ava"
  location            = var.video_analyzer_location
  resource_group_name = var.resource_group_name

  storage_account {
    id                        = azurerm_storage_account.ava.id
    user_assigned_identity_id = azurerm_user_assigned_identity.sv.id
  }

  identity {
    type = "UserAssigned"
    identity_ids = [
      azurerm_user_assigned_identity.sv.id
    ]
  }


  depends_on = [
    azurerm_user_assigned_identity.sv,
    azurerm_role_assignment.contributor,
    azurerm_role_assignment.reader,
  ]

}

resource "azurerm_video_analyzer_edge_module" "sv" {
  name                = "${var.resource_prefix}edgemodule"
  resource_group_name = var.resource_group_name
  video_analyzer_name = azurerm_video_analyzer.sv.name
}