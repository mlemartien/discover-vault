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

The vault can be programmatically unsealed using the API
```bash
curl -X PUT -d '{"key": "unseal_key_1"}' http://127.0.0.1:8200/v1/sys/unseal
curl -X PUT -d '{"key": "unseal_key_2"}' http://127.0.0.1:8200/v1/sys/unseal
curl -X PUT -d '{"key": "unseal_key_3"}' http://127.0.0.1:8200/v1/sys/unseal
```
# Authentication and Authorisation
Authentication is about validating your credentials such as Username/User ID and password to verify one's identity. Authorisation is about validating what resources an authenticated user can or cannot access to.
## Authentication
Vault supports many different authentication mechanisms (LDAP, JWT, username/password, GitHub, etc.), but ultimately they all end up generating what's called a Vault Token. Therefore authentication is simply the process by which a user or machine gets a Vault Token to consume the API with.

This section only covers the direct Vault Token authentication. Other authentication methods are discussed in the Vault [auth method documentation](https://www.vaultproject.io/docs/auth/).

When we initialised the Vault, we obtained a *root* token. This token grants pretty much every permission to the user logging with this token.

One can login using the token by using this command:
```
$ vault login <vault_token>

Success! You are now authenticated. The token information displayed below
is already stored in the token helper. You do NOT need to run "vault login"
again. Future Vault requests will automatically use this token.

Key                  Value
---                  -----
token                s.9b2r9IQXsGJxp0k9Y6520aKD
token_accessor       elEgvgu6OMlBty0pHnzMH8bp
token_duration       ∞
token_renewable      false
token_policies       ["root"]
identity_policies    []
policies             ["root"]
```
The output show which policies the token runs against. The policies define what the user can or cannot do and is discussed in the next section.

New tokens can be created by using this command:
```
$ vault token create

Key                  Value
---                  -----
token                s.V76o2N0mmRDfqNI1FjzfCqLF
token_accessor       q3k0qmcXI1TG1hgcXgRdm8yD
token_duration       ∞
token_renewable      false
token_policies       ["root"]
identity_policies    []
policies             ["root"]
```

The new token becomes a child of the current one and inherit its settings, including the policies. When a *parent* token is revoked, all its children are revoked as well. To revoke a token, simply use command ```vault token revoke <vault_token>```

To see the status of a token, use command ```vault token lookup <vault_token>```
## Authorisation
Authorisation in Vault is implemented by the use of *policies*, written in either JSON or HCL format.

To see a list of policies, use ```vault policy list```. To see the content of a policy, use ```vault policy read <policy_name>```.

### Creating a policy

The policy format is described [here](https://learn.hashicorp.com/vault/identity-access-management/iam-policies).

Use this command to add a new policy to the system:
```bash
$ vault policy write <my_policy_name> <policy_file.hcl>
```

And this one to attach a policy to a new user:
Use this command to add a new policy to the system:
```bash
vault token create -policy=<my_policy_name>
```

# Useful API calls
Enquire the initialisation status of the vault:
```bash
$ curl http://127.0.0.1:8200/v1/sys/init
```
And its overall status:
```bash
$ curl http://127.0.0.1:8200/v1/sys/status
```
# Vault UI
In order to access the UI, make sure that ```ui = true``` has been set in your vault configuration file.
Then access http://127.0.0.1:8200/ui in your favorite browser
# Getting dynamic credentials from Amazon AWS
First enable AWS secret engine:
```bash
$ vault secrets enable aws
```

Add an admin user that Vault can use to create AWS temp users when requested
```bash
$ vault write aws/config/root \
    access_key=AKIAI4SGLQPBX6CSENIQ \
    secret_key=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 \
    region=eu-central-1
```

Then add a role that corresponds to a set of permissions that will be granted to the AWS user that we create on demand. Look at this step like this: *When I ask for a credential for "my-role", create the AWS user and attach the IAM policy { "Version": "2012..." }*.

Let's assume we need a role for saving our backups somewhere on S3. We call it *backuparchiver*:
```bash
$ vault write aws/roles/backuparchiver \
        credential_type=iam_user \
        policy_document=-<<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "s3:PutObject",
        "s3:ListAllMyBuckets",
        "s3:CreateBucket",
        "s3:ListBucket",
        "s3:HeadBucket"
      ],
      "Resource": "*"
    }
  ]
}
EOF
```

Now every time we need to access to AWS for pushing a backup to S3, we will generate a pair of AWS Access Key ID and Secret Key, by running this command
```
$ vault read aws/creds/backuparchiver
Key                Value
---                -----
lease_id           aws/creds/my-role/0bce0782-32aa-25ec-f61d-c026ff22106e
lease_duration     768h
lease_renewable    true
access_key         AKIAJELUDIANQGRXCTZQ
secret_key         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
security_token     <nil>
```
This pair of Key ID and Secret Key is what the script will use to access to S3.
