variable "name" {
  description = "The name of the virtual machine."
  type        = string
}

variable "resource_group_name" {
  description = "Resource group in which to create the virtual machine."
  type        = string
}

variable "location" {
  description = "Azure region for the virtual machine."
  type        = string
}

variable "vm_size" {
  description = "Size of the virtual machine."
  type        = string
  default     = "Standard_B1s"
}

variable "admin_username" {
  description = "Admin username for the virtual machine."
  type        = string
}

variable "ssh_public_key_path" {
  description = "Path to the SSH public key for the virtual machine."
  type        = string
}

variable "network_interface_id" {
  description = "Network interface ID to associate with the virtual machine."
  type        = string
}

variable "tags" {
  description = "Tags to apply to the virtual machine."
  type        = map(string)
  default     = {}
}
