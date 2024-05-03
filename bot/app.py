from __future__ import annotations

import logging

from adapter import AdapterWithErrorHandler
from botbuilder.core import BotFrameworkAdapterSettings
from botbuilder.schema import Activity
from quart import jsonify
from quart import Quart
from quart import request
from quart import Response

from bot import scrumbag_bot

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Quart(__name__)  # Using Quart instead of Flask

# Initialize settings and adapter
SETTINGS = BotFrameworkAdapterSettings(
    '', '',
)  # Fill in with your actual settings
ADAPTER = AdapterWithErrorHandler(SETTINGS)

# Create an instance of the EchoBot
BOT = scrumbag_bot()


@app.route('/api/messages', methods=['POST'])
async def messages():
    # Check if the request content type is JSON
    if 'application/json' not in request.headers['Content-Type']:
        logger.error('Received non-JSON content type')
        return Response('Unsupported media type', status=415)

    body = await request.get_json()  # Asynchronously get JSON data
    logger.info(f"Processing message with body: {body}")

    activity = Activity().deserialize(body)
    auth_header = request.headers.get('Authorization', '')

    try:
        # Ensure this call is awaited
        await ADAPTER.process_activity(activity, auth_header, BOT.on_turn)
        logger.info('Request processed successfully')
        return Response('Handled', status=201)
    except Exception as e:
        logger.exception(f'Failed to process message: {e}', exc_info=True)
        return Response('Internal server error', status=500)

if __name__ == '__main__':
    # Set use_reloader to False if running in debug mode
    app.run(debug=True, port=3978, use_reloader=False)
