data "cloudinit_config" "conf" {
  gzip = false
  base64_encode = false

  part {
    content_type = "text/cloud-config"
    content = file("cloud-config.yaml")
    filename = "cloud-config.yaml"
  }
}
