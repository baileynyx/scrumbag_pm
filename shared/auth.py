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

    # Log the attempt to retrieve the access token
    log_debug_info('Attempting to retrieve access token', url=url, body=body)

    response = requests.post(url, headers=headers, data=body)
    if response.status_code == 200:
        log_message('info', 'Access Token Retrieved Successfully')
        return response.json()['access_token']
    else:
        error_message = f"Failed to retrieve access token: {
            response.status_code
        } {response.text}"
        log_message('error', error_message)
        raise Exception(error_message)


if __name__ == '__main__':
    try:
        token = get_access_token()
        log_message('info', f'Access Token: {token}')
    except Exception as e:
        log_message('error', str(e))
