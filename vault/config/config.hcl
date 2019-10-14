ui = true
disable_clustering = true

storage "dynamodb" {
  ha_enabled = "false"
  region     = "eu-central-1"
  table      = "imrim-vault-data"
}

listener "tcp" {
 address     = "127.0.0.1:8200"
 tls_disable = 1
}