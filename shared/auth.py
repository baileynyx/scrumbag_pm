from __future__ import annotations

import requests
from config import CLIENT_ID
from config import CLIENT_SECRET
from config import TENANT_ID
from utils import log_debug_info
from utils import log_message


def get_access_token():
    url = f"https://login.microsoftonline.com/{TENANT_ID}/oauth2/v2.0/token"
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    body = {
        'grant_type': 'client_credentials',
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        'scope': 'https://graph.microsoft.com/.default',
    }

    log_debug_info('Attempting to retrieve access token', url=url)

    try:
        response = requests.post(url, headers=headers, data=body)
        response.raise_for_status()  # Raises HTTPError for bad responses
        access_token = response.json()['access_token']
        log_message('info', 'Access Token Retrieved Successfully')
        return access_token
    except requests.exceptions.HTTPError as e:
        log_message(
            'error', f'HTTP error occurred: {
                e.response.status_code
            } - {e.response.reason}',
        )
        raise
    except requests.exceptions.RequestException as e:
        log_message('error', f'Error during requests to OAuth endpoint: {e}')
        raise
    except KeyError:
        log_message(
            'error', 'Unexpected response structure from OAuth endpoint.',
        )
        raise


if __name__ == '__main__':
    try:
        token = get_access_token()
        log_message('info', f'Access Token: {token}')
    except Exception as e:
        log_message('error', str(e))
