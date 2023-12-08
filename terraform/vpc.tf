resource "google_compute_network" "vpc_default" {
  name                    = "${var.name}-vpc"
  auto_create_subnetworks = false
  mtu                     = 1460
}

resource "google_compute_subnetwork" "subnet_default" {
  name          = "${var.name}-subnet"
  ip_cidr_range = var.gcp_vpc_subnet_cidr
  region        = var.gcp_region
  network       = google_compute_network.vpc_default.id

  stack_type       = "IPV4_IPV6"
  ipv6_access_type = "EXTERNAL"
}
