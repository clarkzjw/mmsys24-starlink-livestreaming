variable "gcp_project_id" {
  description = "GCP Project ID"
  default     = ""
}

variable "gcp_region" {
  description = "GCP Region"
  default     = "us-west1"
}

variable "gcp_availability_zone" {
  description = "GCP Availability Zone"
  default     = "us-west1-a"
}

variable "name" {
  description = "Project Name"
  default     = "starlink-dashjs-live"
}

variable "gcp_vpc_subnet_cidr" {
  description = "Subnet CIDR"
  default     = "10.0.1.0/24"
}

variable "os_image" {
  description = "VM Image"
  default     = "ubuntu-2304-lunar-amd64-v20230621"
}

variable "os_default_user" {
  description = "Default login user from OS image"
  # default user for Ubuntu is ubuntu
  default = "ubuntu"
}

variable "instance_type" {
  description = "VM Instance Type"
  default     = "g1-small"
}

variable "tag" {
  description = "Tag"
  default     = "starlink"
}

variable "ssh_public_key" {
  description = "SSH Public Key"
  default     = ""
}
