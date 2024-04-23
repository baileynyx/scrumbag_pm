from __future__ import annotations

import os

from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient
from utils import log_debug_info
from utils import log_message

key_vault_name = os.getenv('AZURE_KEY_VAULT_NAME')
if not key_vault_name:
    log_message('error', 'AZURE_KEY_VAULT_NAME environment variable not set.')
    raise ValueError('AZURE_KEY_VAULT_NAME environment variable not set.')

key_vault_url = f"https://{key_vault_name}.vault.azure.net/"
credential = DefaultAzureCredential()
client = SecretClient(vault_url=key_vault_url, credential=credential)


def get_secret(secret_name):
    try:
        secret_value = client.get_secret(secret_name).value
        log_debug_info(
            'Secret retrieved successfully',
            secret_name=secret_name, secret_value=secret_value,
        )
        return secret_value
    except Exception as e:
        log_message(
            'error', f"Failed to retrieve secret {
                secret_name
            }: {str(e)}",
        )
        raise Exception(f"Failed to retrieve secret {secret_name}: {str(e)}")


# Using dashes as Azure Key Vault does not allow underscores in secret names
CLIENT_ID = get_secret('AZURE-CLIENT-ID')
CLIENT_SECRET = get_secret('AZURE-CLIENT-SECRET')
TENANT_ID = get_secret('AZURE-TENANT-ID')
