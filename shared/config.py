from __future__ import annotations

import os

from azure.core.exceptions import ClientAuthenticationError
from azure.core.exceptions import HttpResponseError
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient
from utils import log_message

# Key Vault setup
key_vault_name = os.getenv('AZURE_KEY_VAULT_NAME')
if not key_vault_name:
    log_message('error', 'AZURE_KEY_VAULT_NAME environment variable not set.')
    raise OSError('AZURE_KEY_VAULT_NAME environment variable not set.')
key_vault_url = f"https://{key_vault_name}.vault.azure.net/"

# Azure Credentials
credential = DefaultAzureCredential()
client = SecretClient(vault_url=key_vault_url, credential=credential)


def get_secret(secret_name: str) -> str:
    try:
        # For security reasons, consider commenting out the below log in a production environment
        # log_message('info', f"Retrieving secret: {secret_name}")
        return client.get_secret(secret_name).value
    except HttpResponseError as http_error:
        log_message(
            'error', f"HTTP error occurred while retrieving secret {
                secret_name
            }: {http_error.message}",
        )
        raise
    except ClientAuthenticationError as auth_error:
        log_message(
            'error', f"Authentication error occurred while retrieving secret {
                secret_name
            }: {auth_error.message}",
        )
        raise
    except Exception as e:
        log_message(
            'error', f"Unexpected error occurred while retrieving secret {
                secret_name
            }: {e}",
        )
        raise


# Fetch and set all the necessary secrets as global variables
CLIENT_ID = get_secret('AZURE-CLIENT-ID')
CLIENT_SECRET = get_secret('AZURE-CLIENT-SECRET')
TENANT_ID = get_secret('AZURE-TENANT-ID')
MICROSOFT_APP_ID = get_secret('APP-ID')
MICROSOFT_APP_PASSWORD = get_secret('APP-PASSWORD')
CLU_ENDPOINT = get_secret('CLU-ENDPOINT')
CLU_SECRET = get_secret('CLU-SECRET')
# ... add any other secrets here as needed
