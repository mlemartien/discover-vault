import os
import sys
import getopt
import json
import argparse

import boto3
import requests
from requests.exceptions import HTTPError
import pyAesCrypt


class ImrimVault:
    def __init__(self, vault_host="http://127.0.0.1:8200"):
        self.vault_host = vault_host 
        self.vault_token = os.environ["VAULT_TOKEN"]


    def run_api(self, path, verb="GET", payload=""):
        try:
            if verb == "GET":
                response = requests.get(
                    f"{self.vault_host}/{path}",
                    headers={"X-Vault-Token": self.vault_token}
                )
            
            elif verb == "POST":
                response = requests.post(
                    f"{self.vault_host}/{path}",
                    headers={"X-Vault-Token": self.vault_token},
                    data=payload
                )                

            elif verb == "PUT":
                response = requests.post(
                    f"{self.vault_host}/{path}",
                    headers={"X-Vault-Token": self.vault_token},
                    data=payload
                )                

        except HTTPError as http_err:
            print(f'HTTP error occurred: {http_err}')

        except Exception as err:
            print(f'Other error occurred: {err}')

        return response        


    def is_sealed(self):
        sealed = True

        response = self.run_api("v1/sys/seal-status")
        if response:
            sealed = response.json()["sealed"]
        else:
            print(f"Could not determine the seal status of the vault: error {response.status_code}")
        
        return sealed


    def unseal_vault(self, key1, key2, key3):
        try:
            self.run_api("v1/sys/unseal", "PUT", "{'key': {}}".format(key1))
            self.run_api("v1/sys/unseal", "PUT", "{'key': {}}".format(key2))
            self.run_api("v1/sys/unseal", "PUT", "{'key': {}}".format(key3))

        except Exception as e:
            pass

        return (self.is_sealed() == False)
        

    def get_encryption_data_key(self, key_id):
        response = self.run_api(verb="POST", path=f"v1/transit/datakey/plaintext/{key_id}")
        return response


    def decrypt(self, key_id, ciphertext):
        response = self.run_api(
            verb="POST",
            path=f"v1/transit/decrypt/{key_id}",
            payload={
                "ciphertext": ciphertext
            }
        )
        return response["data"]["plaintext"]


    def get_aws_credentials(self, aws_role):
        response = self.run_api(f"v1/aws/creds/{aws_role}")
        return (
            response.json()["data"]["access_key"],
            response.json()["data"]["secret_key"],
            response.json()["lease_duration"],
            response.json()["lease_id"]
        )


    def release_aws_credentials(self, lease_id):
        response = self.run_api(f"v1/sys/leases/revoke/{lease_id}", "PUT")
        return response


def main(*args):
    parser = argparse.ArgumentParser(description='A demo script to play with Hashicorp Vault!')
    parser.add_argument(
        "--mode",
        default="encrypt",
        choices=["encrypt", "decrypt"],
        help="Execution mode - encrypt or decrypt"
    )
    args = parser.parse_args()

    # Some working variables
    encryption_vault_master_key_id = "backup_files"
    aws_credentials_role = "backup_archiver"
    destination_s3_bucket = "imrim-confluence-postgres-backup"
    file_to_encrypt = "backup.sql"
    file_encrypted = f"{file_to_encrypt}.encrypted"    
    file_encrypted_downloaded = f"{file_to_encrypt}.encrypted.downloaded" 
    file_decrypted_downloaded = f"{file_to_encrypt}.decrypted.downloaded" 

    # Get an instance of the vault object
    imrim_vault = ImrimVault()

    print(f"\n")
    input("Press [Enter] to check if the Vault is open...")

    is_vault_sealed = imrim_vault.is_sealed()
    print("The vault is {}.\n".format("sealed" if is_vault_sealed else "open"))
    if is_vault_sealed:
        quit()

    if args.mode == "encrypt":

        # 
        input("Press [Enter] to obtain an Encryption Data Key...")
        response = imrim_vault.get_encryption_data_key(encryption_vault_master_key_id)
        plaintext_key = response.json()['data']['plaintext']
        ciphertext_key = response.json()['data']['ciphertext']
        print(f"Plain text key: {plaintext_key}")
        print(f"Encrypted key: {ciphertext_key}\n")

        #
        input("Press [Enter] to encrypt the backup file...")
        buffer_size = 65536
        pyAesCrypt.encryptFile(
            file_to_encrypt,
            file_encrypted,
            plaintext_key,
            buffer_size
        )
        print(f"File {file_to_encrypt} has been encrypted.\n")

        #
        input("Press [Enter] to obtain a dynamic AWS login...")
        aws_access = imrim_vault.get_aws_credentials("backup_archiver")
        print(f"AWS Credentials Lease ID: {aws_access[3]}")
        print(f"AWS Credentials valid for: {aws_access[2]} seconds")
        print(f"AWS API Access Key ID: {aws_access[0]}")
        print(f"AWS API Access Secret: ********************************\n")

        s3_client = boto3.client(
            's3',
            aws_access_key_id=aws_access[0],
            aws_secret_access_key=aws_access[1]
        )

        # Send the file to S3
        input("Press [Enter] to send the (encrypted) file to  Amazon S3 along with the encrypted Data Key...")
        try:
            s3_client.upload_file(
                "./" + file_encrypted,
                destination_s3_bucket,
                file_encrypted,
                ExtraArgs={
                    "ServerSideEncryption": "AES256",
                    "StorageClass": "STANDARD_IA"
                }
            )

        except Exception as e:
            print(f"Could not upload the file: {e}")
            quit()

        try:
            response = s3_client.put_object_tagging(
                Bucket=destination_s3_bucket,
                Key=file_encrypted,
                Tagging={
                    "TagSet": [
                        {
                            "Key": "DataKey",
                            "Value": ciphertext_key
                        },
                        {
                            "Key": "MasterKeyID",
                            "Value": encryption_vault_master_key_id
                        }                
                    ]
                }
            )

        except Exception as e:
            print(f"Could not tag the file: {e}")
            quit()

        print("The file has been uploaded and tagged with the encrypted Data Key\n")

    else:

        #
        input("Press [Enter] to obtain a dynamic AWS login...")
        aws_access = imrim_vault.get_aws_credentials("backup_retriever")
        print(f"AWS Credentials Lease ID: {aws_access[3]}")
        print(f"AWS Credentials valid for: {aws_access[2]} seconds")
        print(f"AWS API Access Key ID: {aws_access[0]}")
        print(f"AWS API Access Secret: ********************************\n")

        s3_client = boto3.client(
            's3',
            aws_access_key_id=aws_access[0],
            aws_secret_access_key=aws_access[1]
        )

        #
        input("Press [Enter] to download the backup file...")
        try:
            s3_client.download_file(
                destination_s3_bucket,
                file_encrypted,
                f"./{file_encrypted_downloaded}"
            )

        except Exception as e:
            print(f"Could not download the file: {e}")
            quit()

        try:
            response = s3_client.get_object_tagging(
                Bucket=destination_s3_bucket,
                Key=file_encrypted
            )

        except Exception as e:
            print(f"Could not retrieve the tags of the file: {e}")
            quit()

        print(f"File downloaded into {file_encrypted_downloaded}")
        for tag in response["TagSet"]:
            print(f"{tag['Key']}: {tag['Value']}")
            if tag["Key"] == "DataKey":
                ciphertext_key = tag["Value"]
            elif tag["Key"] == "MasterKeyID":
                encryption_vault_master_key_id = tag["Value"]

        print(f"\n")

        #
        input("Press [Enter] to ask Vault to decrypt our Data Key")
        decrypted_data_key = imrim_vault.decrypt(encryption_vault_master_key_id, ciphertext_key)
        printf("The decrypted Data Key is: {}")

        
    # Release the AWS lease
    input("Press [Enter] to release the dynamic AWS login...")
    response = imrim_vault.release_aws_credentials(aws_access[3])
    print("The AWS Credentials lease has been revoked\n")
    

if __name__ == '__main__':
    main(sys.argv)