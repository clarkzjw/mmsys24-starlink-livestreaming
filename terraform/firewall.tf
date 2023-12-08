resource "google_compute_firewall" "ssh" {
  name = "ssh"
  allow {
    ports    = ["22"]
    protocol = "tcp"
  }
  direction     = "INGRESS"
  network       = google_compute_network.vpc_default.id
  priority      = 1000
  source_ranges = ["0.0.0.0/0"]
  target_tags   = [var.tag]
}

resource "google_compute_firewall" "iperf3" {
  name    = "iperf3"
  network = google_compute_network.vpc_default.id

  allow {
    protocol = "tcp"
    ports    = ["5201"]
  }
  allow {
    protocol = "udp"
    ports    = ["5201"]
  }
  source_ranges = ["0.0.0.0/0"]
}

resource "google_compute_firewall" "irtt" {
  name    = "irtt"
  network = google_compute_network.vpc_default.id

  allow {
    protocol = "tcp"
    ports    = ["2112"]
  }
  allow {
    protocol = "udp"
    ports    = ["2112"]
  }
  source_ranges = ["0.0.0.0/0"]
}

resource "google_compute_firewall" "icmp" {
  name    = "icmp"
  network = google_compute_network.vpc_default.id

  allow {
    protocol = "icmp"
  }
  source_ranges = ["0.0.0.0/0"]
}

resource "google_compute_firewall" "http" {
  name    = "http"
  network = google_compute_network.vpc_default.id

  allow {
    protocol = "udp"
    ports = ["443", "80", "8443"]
  }
  allow {
    protocol = "tcp"
    ports = ["443", "80", "8443"]
  }
  
  source_ranges = ["0.0.0.0/0"]
}
