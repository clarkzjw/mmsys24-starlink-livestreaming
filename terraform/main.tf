provider "google" {
  project = var.gcp_project_id
  region  = var.gcp_region
  zone    = var.gcp_availability_zone
}

resource "google_compute_instance" "vm_default" {
  name         = "${var.name}-server"
  machine_type = var.instance_type
  zone         = var.gcp_availability_zone
  tags         = [var.tag]

  boot_disk {
    initialize_params {
      image = var.os_image
      size = 100
    }
  }

  metadata = {
    ssh-keys = "ubuntu:${google_os_login_ssh_public_key.ssh_pubkey_default.key}"
    user-data = data.cloudinit_config.conf.rendered
  }

  network_interface {
    subnetwork = google_compute_subnetwork.subnet_default.id

    access_config {
      # Include this section to give the VM an ephemeral external IP address
    }
  }
}

output "public_ip" {
  description = "Public IP of virtual machine"
  value       = google_compute_instance.vm_default.network_interface[0].access_config[0].nat_ip
  sensitive   = false
}
