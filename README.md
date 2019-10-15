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
  --volume ~/.aws/:/home/vault/.aws:ro \
  --volume ~/Documents/Dev/discover-vault/vault:/vault \
  --cap-add=IPC_LOCK vault server




VAULT_ADDR vs. VAULT_API_ADDR

VAULT_API_ADDR is only used when the "cluster" mode is active (aka high availability, enabled by default in server mode). It advertises to the Vault cluster nodes on the address to redirect clients to 
### Which Vault client?
## Running inside the container
## Executing inside the container
You can prefix all your commands with:
```bash
$ docker exec -it imrim_vault <vault_command_to_execute>
```
This will execute the vault command directly inside the container. Option ```-it``` requests Docker to execute the command in interactive mode. For example, run the following command to (partially) unseal the vault:
```bash
$ docker exec -it imrim_vault vault operator unseal 8acfqex1GEaoSsCFSchtlEuQd7Cx5IQiLcjMqMkxfw
```
# Getting started with the vault
## Show status of the vault
Use your vault client and type:
```bash
$ vault status
```
Should return something along those lines:
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
## Initialise the vault
Now we will initialise the vault:
 ```bash
$ vault operator init
```
You should get this output:
```
Unseal Key 1: EI2h+k9VfGtptDJJwBT3YjK9z8myvyUFY1mbSoLrd/
Unseal Key 2: FmO0sG5El49xNahGKBIqcwm4bZE2Fd22HSwUwSmwrN
Unseal Key 3: jKaE314liqQqjNeRgrzDtPcA9YAxBdFMv/GWU6xpYEi
Unseal Key 4: PNZYGiepKDbPKSs9pXceOR3Yj23OcfTU77oj6HByBN
Unseal Key 5: 8acfqex1GEaoSsCFSchtlEuQd7Cx5IQiLcjMqMkxfw

Initial Root Token: s.9b2r9IQXsGJxp0k9Y6520aKD

Vault initialized with 5 key shares and a key threshold of 3. Please securely
distribute the key shares printed above. When the Vault is re-sealed,
restarted, or stopped, you must supply at least 3 of these keys to unseal it
before it can start servicing requests.

Vault does not store the generated master key. Without at least 3 key to
reconstruct the master key, Vault will remain permanently sealed!

It is possible to generate new unseal keys, provided you have a quorum of
existing unseal keys shares. See "vault operator rekey" for more information.
```
At this point, it is essential you save the five Unseal Keys. The vault will be forever sealed if they are lost.
## Unseal the vault
Now that the vault is initialised, we need to unseal it. Type the following command to unseal it:
```bash
$ vault operator unseal
```
Vault will display the status again and you should watch the ```Unseal Progress``` line. It indicates how many unseal keys have been entered so far. Remember that we need to enter 3 keys to completely unseal the vault.
```
Key                Value
---                -----
Seal Type          shamir
Initialized        true
Sealed             true
Total Shares       5
Threshold          3
Unseal Progress    1/3
Unseal Nonce       092e3223-2eec-c67b-e1a0-24fb22e63af0
Version            1.2.3
HA Enabled         false
```
Re-enter the same ```vault operator unseal```until you successfully entered 3 out of 5 unseal keys. When that happens, the line ```Sealed``` will show a status of ```false``` (see below). At this stage we can also see additional information like the cluser name and cluster id.
```
Key             Value
---             -----
Seal Type       shamir
Initialized     true
Sealed          false
Total Shares    5
Threshold       3
Version         1.2.3
Cluster Name    vault-cluster-84109cc1
Cluster ID      337764d6-9977-97f5-887b-f5331a449f0f
HA Enabled      false
```

| The vault can be unsealed from multiple computers and the keys should never be together. A single malicious operator does not have enough keys to be malicious. |
| --- |

### Vault UI
In order to access the UI, make sure that ```ui = true``` has been set in your vault configuration file.
Then access https://127.0.0.1:8200/ui in your favorite browser
