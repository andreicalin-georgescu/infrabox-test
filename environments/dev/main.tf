# This module manages the Dev environment.

module "resource_group" {
  source   = "../../modules/resource_group"
  name     = "${var.name_prefix}-${var.environment}-RG"
  location = var.location
  tags     = var.tags
}

module "networking" {
  source                  = "../../modules/networking"
  name                    = "${var.name_prefix}-${var.environment}"
  location                = var.location
  resource_group_name     = module.resource_group.resource_group_name
  dns_zone_name           = var.dns_zone_name
  vnet_address_space      = ["10.0.0.0/16"]
  subnet_address_prefixes = ["10.0.1.0/24"]
  tags                    = var.tags
}

module "virtual_machine" {
  source               = "../../modules/virtual_machine"
  name                 = "${var.name_prefix}-VM"
  resource_group_name  = module.resource_group.resource_group_name
  location             = var.location
  vm_size              = "Standard_B1s"
  admin_username       = "${var.admin_username}-${var.environment}"
  ssh_public_key_path  = var.ssh_public_key_path
  network_interface_id = module.networking.network_interface_id
  tags                 = var.tags
}

module "storage_account" {
  source                   = "../../modules/storage_account"
  name                     = lower(replace("${var.name_prefix}-${var.environment}-SA01", "-", ""))
  resource_group_name      = module.resource_group.resource_group_name
  location                 = var.location
  account_tier             = "Standard"
  account_replication_type = "LRS"
  tags                     = var.tags
}
