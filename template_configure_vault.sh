#!/bin/bash

# Init vault
docker exec -it imrim_vault vault operator init

# Unseal the vault
docker exec -it imrim_vault vault operator unseal
docker exec -it imrim_vault vault operator unseal
docker exec -it imrim_vault vault operator unseal

# Login using root token
docker exec -it imrim_vault vault login <...>

# Enable transit engine
docker exec -it imrim_vault vault secrets enable transit

# Create a master key for backup_files
docker exec -it imrim_vault vault write -f transit/keys/backup_files

# Enable aws engine
docker exec -it imrim_vault vault secrets enable aws

# Create credentials for vault to communicate with AWS
docker exec -it imrim_vault vault write aws/config/root \
    access_key=<...> \
    secret_key=<...> \
    region=eu-central-1

# Configure vault role for backup_archivers
docker exec -it imrim_vault vault write aws/roles/backup_archiver \
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
                "s3:HeadBucket",
                "s3:PutObjectTagging"
            ],
            "Resource": "*"
        }
    ]
}
EOF

docker exec -it imrim_vault vault write aws/roles/backup_retriever \
    credential_type=iam_user \
    policy_document=-<<EOF
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "s3:GetObject",
                "s3:ListAllMyBuckets",
                "s3:ListBucket",
                "s3:HeadBucket",
                "s3:GetObjectTagging"
            ],
            "Resource": "*"
        }
    ]
}
EOF

