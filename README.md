# discover-vault
Playing around with Hashicorp Vault


## Prep work

Create config directory
mkdir config


The AWS API configuration sits in ~/.aws

credentials has the API key id and secrets
config has settings like default region, output format


Start container

At startup, the server will read configuration HCL and JSON files from /vault/config

docker run --rm \
  --name imrim_vault \
  --env AWS_PROFILE=jacques \
  --env VAULT_API_ADDR=http://127.0.0.1:8200 \
  --publish 8200:8200 \
  --publish 8500:8500 \
  --volume ~/.aws/:/home/vault/.aws:ro \
  --volume ~/Documents/Dev/discover-vault/vault:/vault \
  --cap-add=IPC_LOCK vault server
