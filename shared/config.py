from __future__ import annotations

import logging
from http import HTTPStatus

from quart import Quart
from quart import request
from quart import Response

from .auth import get_secret  # Adjusted import statement to relative import
from .utils import log_debug_info
from .utils import log_message

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Retrieve secrets from Azure Key Vault
MICROSOFT_APP_ID = get_secret('APP-ID')
MICROSOFT_APP_PASSWORD = get_secret('APP-PASSWORD')
CLU_ENDPOINT = get_secret('CLU-ENDPOINT')
CLU_SECRET = get_secret('CLU-SECRET')
CLU_PROJECT_NAME = get_secret('CLU-PROJECT-NAME')

app = Quart(__name__)  # Using Quart instead of Flask

# Initialize settings using configuration constants
# This avoids the need to import the bot directly here, reducing circular import risk

@app.route('/api/messages', methods=['POST'])
async def messages():
    if 'application/json' not in request.headers['Content-Type']:
        logger.error('Received non-JSON content type')
        return Response('Unsupported media type', status=HTTPStatus.UNSUPPORTED_MEDIA_TYPE)

    try:
        body = await request.get_json()  # Asynchronously get JSON data
        logger.info(f"Processing message with body: {body}")

        # Avoid direct import of bot to prevent circular imports
        # Import dynamically when it's actually needed inside the function
        from bot import scrumbag_bot

        activity = Activity().deserialize(body)
        auth_header = request.headers.get('Authorization', '')

        await scrumbag_bot.process_activity(activity, auth_header)
        logger.info('Request processed successfully')
        return Response('Handled', status=HTTPStatus.CREATED)
    except Exception as e:
        logger.exception('Failed to process message', exc_info=True)
        return Response('Internal server error', status=HTTPStatus.INTERNAL_SERVER_ERROR)

if __name__ == '__main__':
    app.run(debug=False, port=3978, use_reloader=False)
