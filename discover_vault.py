import os
import json

import boto3
import requests
from requests.exceptions import HTTPError
from Crypto.Cipher import AES
import pyAesCrypt


class ImrimVault:
    def __init__(self, vault_host="http://127.0.0.1:8200"):
        self.vault_host = vault_host 
        self.vault_token = os.environ["VAULT_TOKEN"]


    def run_api(self, path, verb="GET", data=""):
        try:
            if verb == "GET":
                response = requests.get(
                    f"{self.vault_host}/{path}",
                    headers={"X-Vault-Token": self.vault_token}
                )
            
            elif verb == "POST":
                response = requests.post(
                    f"{self.vault_host}/{path}",
                    headers={"X-Vault-Token": self.vault_token}
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

    def get_encryption_data_key(self, key_id):
        response = self.run_api(verb="POST",path=f"v1/transit/datakey/plaintext/{key_id}")
        return response





def main():
    # Least privelege
    # Encrypt everything
    # Manage data lifecycle

    imrim_vault = ImrimVault()


    # input("Press [Enter] to check if we have backup files to archive...")

    input("Press [Enter] to check if the Vault is open...")

    is_vault_sealed = imrim_vault.is_sealed()
    print("The vault is {}.\n".format("sealed" if is_vault_sealed else "open"))
    if is_vault_sealed:
        quit()

    # input("Press [Enter] to log to the Vault...")


    input("Press [Enter] to obtain an Encryption Data Key...")
    
    response = imrim_vault.get_encryption_data_key("backup_files")
    plaintext_key = response.json()['data']['plaintext']
    ciphertext_key = response.json()['data']['ciphertext']
    print(f"Plain text key: {plaintext_key}")
    print(f"Encrypted key: {ciphertext_key}\n")

    input("Press [Enter] to encrypt the backup file...")
    
    file_to_encrypt = "backup.sql"
    buffer_size = 65536
    pyAesCrypt.encryptFile(file_to_encrypt, f"{file_to_encrypt}.aes", password, bufferSize)

    # # Open the input and output files
    # input_file = open(file_to_encrypt, "rb")
    # output_file = open(f"{file_to_encrypt}.encrypted", "wb")

    # # Create the cipher object and encrypt the data
    # cipher_encrypt = AES.new(plaintext_key, AES.MODE_CFB)

    # # Initially write the iv to the output file
    # output_file.write(cipher_encrypt.iv)

    # # Keep reading the file into the buffer, encrypting then writing to the new file
    # buffer = input_file.read(buffer_size)
    # while len(buffer) > 0:
    #     ciphered_bytes = cipher_encrypt.encrypt(buffer)
    #     output_file.write(ciphered_bytes)
    #     buffer = input_file.read(buffer_size)

    # # Close the input and output files
    # input_file.close()
    # output_file.close()

    # input("Press [Enter] to obtain a dynamic AWS login...")
    # input("Press [Enter] to connect to Amazon S3...")
    # input("Press [Enter] to send the (encrypted) file to  Amazon S3...")
    # input("Press [Enter] to release the dynamic AWS login...")
    

if __name__ == '__main__':
    main()