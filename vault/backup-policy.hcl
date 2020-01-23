# Permit creating a temporary AWS IAM user starting with "backup-"
path "secret/aws/backup-*" {
  capabilities = [ "create" ]
}
 
# Permit creating a data encryption envelope for master keys ending with "-backup"
path "secret/transit/*-backup" {
  capabilities = [ "create" ]
}