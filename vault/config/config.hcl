// General settings
cluster_name = "imrim_vault"
log_level = "debug"
ui = true
disable_clustering = true

// Leveraging AWS DynamoDB as a storage for Vaul. Offers native HA
// We authenticate to AWS by passing the API Consumer Profile name
// and mounting the [~/.aws] folder into the container. If we ran
// Vault in an EC2 instance, we would use IAM EC2 roles instead
storage "dynamodb" {
  ha_enabled = "false"
  region     = "eu-central-1"
  table      = "imrim-vault-data-2"
}

// Note the 0.0.0.0 binding; this is to let curl and other clients to
// access to Vault running inside the container from the Docker host
// Production grade Vault deployment should not disable TLS, of course
listener "tcp" {
 address     = "0.0.0.0:8200"
 tls_disable = 1
//  tls_cert_file = 
//  tls_key_file =
//  tls_min_version = "tls12"
}
