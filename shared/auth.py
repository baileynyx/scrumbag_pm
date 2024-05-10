from __future__ import annotations

import requests
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient

from .utils import log_debug_info
from .utils import log_message


# Initialize the Azure Key Vault client
key_vault_url = 'https://<your-key-vault-name>.vault.azure.net/'
credential = DefaultAzureCredential()
client = SecretClient(vault_url=key_vault_url, credential=credential)

def get_secret(secret_name: str) -> str:
    try:
        retrieved_secret = client.get_secret(secret_name)
        log_message('info', f'Successfully retrieved {secret_name}')
        return retrieved_secret.value
    except Exception as e:
        log_message('error', f'Failed to retrieve {secret_name}: {str(e)}')
        raise

def get_access_token():
    tenant_id = get_secret('azure-tenant-id')
    client_id = get_secret('azure-client-id')
    client_secret = get_secret('azure-client-secret')

    url = f"https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token"
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    body = {
        'grant_type': 'client_credentials',
        'client_id': client_id,
        'client_secret': client_secret,
        'scope': 'https://graph.microsoft.com/.default',
    }

    log_debug_info('Attempting to retrieve access token')

    try:
        response = requests.post(url, headers=headers, data=body)
        response.raise_for_status()  # Raises HTTPError for bad responses
        access_token = response.json()['access_token']
        log_message('info', 'Successfully authenticated with Azure.')
        return access_token
    except requests.exceptions.HTTPError as e:
        log_message(
            'error', f'HTTP error occurred: {e.response.status_code} - {e.response.reason}', exc_info=True
        )
        raise
    except requests.exceptions.RequestException as e:
        log_message('error', f'Error during requests to OAuth endpoint: {str(e)}', exc_info=True)
        raise
    except KeyError:
        log_message('error', 'Unexpected response structure from OAuth endpoint.')
        raise

if __name__ == '__main__':
    try:
        token = get_access_token()
        # For security reasons, avoid logging the actual token
        log_message('info', 'Access token retrieved and available for use.')
    except Exception as e:
        log_message('error', str(e))
