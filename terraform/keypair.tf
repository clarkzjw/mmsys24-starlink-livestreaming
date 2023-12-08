data "google_client_openid_userinfo" "me" {
}

resource "google_os_login_ssh_public_key" "ssh_pubkey_default" {
  project = var.gcp_project_id
  user    = data.google_client_openid_userinfo.me.email
  key     = var.ssh_public_key
}
