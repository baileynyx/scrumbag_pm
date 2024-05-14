# Import necessary libraries for handling Azure authentication and secrets management
from __future__ import annotations

import logging
import os

from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient
from dotenv import load_dotenv

# Set up basic configuration for logging to help in debugging and monitoring the application
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

# Load environment variables from a .env file located in the same directory as this script
# This is particularly useful in development environments or when sensitive credentials
# are not to be hard-coded in the source code.
load_dotenv()

# Retrieve the name of the Azure Key Vault from environment variables
# This requires setting the 'AZURE_KEY_VAULT_NAME' in your environment or .env file
key_vault_name = os.getenv('AZURE_KEY_VAULT_NAME')
if not key_vault_name:
    logging.error('Azure Key Vault name not provided in environment variables.')
    raise OSError('Azure Key Vault name not specified.')

# Construct the URL needed to access the Azure Key Vault
vault_url = f"https://{key_vault_name}.vault.azure.net"

# Initialize Azure credentials using DefaultAzureCredential which automatically uses the available authentication methods
# DefaultAzureCredential supports various authentication methods including system-assigned managed identities, user-assigned
# managed identities, development tools, and more, making it flexible for both development and production environments.
credential = DefaultAzureCredential()

# Initialize the Key Vault client using the credentials obtained above and the Key Vault URL
# This client will be used to retrieve secrets stored in the Azure Key Vault
client = SecretClient(vault_url=vault_url, credential=credential)

def get_secret(secret_name: str) -> str:
    """
    Retrieves a secret from Azure Key Vault.

    Parameters:
    secret_name (str): The name of the secret to retrieve.

    Returns:
    str: The value of the retrieved secret.

    Raises:
    Exception: If the secret cannot be retrieved due to configuration errors, network issues, or Azure permissions.
    """
    try:
        # Retrieve the secret using the secret name provided
        retrieved_secret = client.get_secret(secret_name)
        logging.info(f"Successfully retrieved secret: {secret_name}")
        return retrieved_secret.value
    except Exception as e:
        # Log and re-raise exceptions to ensure that they can be handled or logged appropriately upstream
        logging.error(f"Failed to retrieve secret '{secret_name}': {str(e)}")
        raise
import requests  # Import requests to handle HTTP requests to Azure AD

def get_access_token(tenant_id: str, client_id: str, client_secret: str, scope: str = 'https://graph.microsoft.com/.default') -> str:
    """
    Obtains an access token from Azure Active Directory using client credentials.

    Parameters:
    tenant_id (str): The Azure AD tenant ID.
    client_id (str): The application (client) ID registered in Azure AD.
    client_secret (str): The application secret for the client ID.
    scope (str): The scope for which the access token is valid. Default is for Microsoft Graph API.

    Returns:
    str: An access token as a string.

    Raises:
    HTTPError: If an HTTP error occurs during the token acquisition.
    """
    # Construct the URL for obtaining the token
    token_url = f"https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token"

    # Define the headers and body of the request
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    body = {
        'grant_type': 'client_credentials',
        'client_id': client_id,
        'client_secret': client_secret,
        'scope': scope
    }

    # Log the attempt to retrieve the access token for auditing and monitoring purposes
    logging.info('Attempting to retrieve access token from Azure AD')

    try:
        # Send a POST request to obtain the token
        response = requests.post(token_url, headers=headers, data=body)
        response.raise_for_status()  # Raises HTTPError for bad responses
        # Extract the access token from the response
        access_token = response.json()['access_token']
        logging.info('Successfully authenticated with Azure AD and retrieved access token.')
        return access_token
    except requests.exceptions.HTTPError as e:
        logging.error(f"HTTP error occurred while obtaining access token: {e.response.status_code} - {e.response.reason}")
        raise
    except requests.exceptions.RequestException as e:
        # Generic error handling for any issue related to the request
        logging.error(f"Error occurred while obtaining access token: {str(e)}")
        raise

if __name__ == '__main__':
    # Example usage: This block is typically only included for testing purposes and would be removed or disabled in production.
    try:
        # Retrieve tenant ID, client ID, and client secret from Azure Key Vault or environment variables for security
        tenant_id = get_secret('azure-tenant-id')
        client_id = get_secret('azure-client-id')
        client_secret = get_secret('azure-client-secret')

        # Get an access token for Microsoft Graph API
        token = get_access_token(tenant_id, client_id, client_secret)
        logging.info('Access token retrieved and available for use.')
    except Exception as e:
        logging.error(f"An error occurred in the main execution block: {str(e)}")
