# discover-vault
Playing around with Hashicorp Vault


## Prep work

Create config directory
mkdir config

2 modes
server mode (persistant, ui off by default)
dev mode (in memory, ui on)

The AWS API configuration sits in ~/.aws
credentials has the API key id and secrets
config has settings like default region, output format


Start container

At startup, the server will read configuration HCL and JSON files from /vault/config

docker run --rm \
  --name imrim_vault \
  --env AWS_PROFILE=jacques \
  --env VAULT_ADDR=http://127.0.0.1:8200 \
  --env VAULT_API_ADDR=http://127.0.0.1:8200 \
  --publish 8200:8200 \
  --publish 8500:8500 \
  --volume ~/.aws/:/home/vault/.aws:ro \
  --volume ~/Documents/Dev/discover-vault/vault:/vault \
  --cap-add=IPC_LOCK vault server


VAULT_ADDR vs. VAULT_API_ADDR

VAULT_API_ADDR is only used when the "cluster" mode is active (aka high availability, enabled by default in server mode). It advertises to the Vault cluster nodes on the address to redirect clients to 



```
Key                Value
---                -----
Seal Type          shamir
Initialized        false
Sealed             true
Total Shares       0
Threshold          0
Unseal Progress    0/0
Unseal Nonce       n/a
Version            n/a
HA Enabled         false
```