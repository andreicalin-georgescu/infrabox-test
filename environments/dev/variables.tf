variable "name_prefix" {
  type    = string
  default = "InfraBox"
}

variable "environment" {
  type    = string
  default = "Dev"
}

variable "location" {
  type    = string
  default = "westeurope"
}

variable "dns_zone_name" {
  type    = string
  default = "infrabox-dev.com"
}

variable "admin_username" {
  type    = string
  default = "azureuser"
}

variable "ssh_public_key_path" {
  type    = string
  default = "~/.ssh/id_rsa_infrabox.pub"
}

variable "tags" {
  type = map(string)
  default = {
    project     = "InfraBox"
    environment = "Dev"
  }
}
