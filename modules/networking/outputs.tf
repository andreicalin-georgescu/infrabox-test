output "subnet_id" {
  value = azurerm_subnet.this.id
}

output "network_interface_id" {
  value = azurerm_network_interface.this.id
}

output "public_ip" {
  value = azurerm_public_ip.this.ip_address
}

output "dns_zone_name" {
  value = azurerm_dns_zone.this.name
}
