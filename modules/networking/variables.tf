variable "name" {
  description = "Name for the networking resources"
  type        = string
}

variable "location" {
  description = "Azure region for all resources"
  type        = string
}

variable "resource_group_name" {
  description = "Resource group in which to create networking resources"
  type        = string
}

variable "dns_zone_name" {
  description = "DNS zone name (e.g. infrabox-dev.com)"
  type        = string
}

variable "vnet_address_space" {
  description = "Address space for the virtual network"
  type        = list(string)
  default     = ["10.0.0.0/16"]
}

variable "subnet_address_prefixes" {
  description = "Subnet address range within the VNet"
  type        = list(string)
  default     = ["10.0.1.0/24"]
}

variable "tags" {
  description = "Tags to apply to the networking resources"
  type        = map(string)
  default     = {}
}
