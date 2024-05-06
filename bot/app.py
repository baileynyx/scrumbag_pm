from __future__ import annotations

import logging
from http import HTTPStatus

from adapter import AdapterWithErrorHandler
from botbuilder.core import BotFrameworkAdapterSettings
from botbuilder.schema import Activity
from quart import jsonify
from quart import Quart
from quart import request
from quart import Response

from bot import scrumbag_bot
from shared.config import MICROSOFT_APP_ID
from shared.config import MICROSOFT_APP_PASSWORD
from shared.utils import log_message

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Quart(__name__)  # Using Quart instead of Flask

# Initialize settings and adapter using shared config
SETTINGS = BotFrameworkAdapterSettings(MICROSOFT_APP_ID, MICROSOFT_APP_PASSWORD)
ADAPTER = AdapterWithErrorHandler(SETTINGS)

# Create an instance of the bot
BOT = scrumbag_bot()

@app.route('/api/messages', methods=['POST'])
async def messages():
    if 'application/json' not in request.headers['Content-Type']:
        logger.error('Received non-JSON content type')
        return Response('Unsupported media type', status=HTTPStatus.UNSUPPORTED_MEDIA_TYPE)

    try:
        body = await request.get_json()  # Asynchronously get JSON data
        logger.info(f"Processing message with body: {body}")

        activity = Activity().deserialize(body)
        auth_header = request.headers.get('Authorization', '')

        await ADAPTER.process_activity(activity, auth_header, BOT.on_turn)
        logger.info('Request processed successfully')
        return Response('Handled', status=HTTPStatus.CREATED)
    except KeyError as e:
        logger.exception('Key error in processing the request', exc_info=True)
        return Response(f'Key error: {str(e)}', status=HTTPStatus.BAD_REQUEST)
    except ValueError as e:
        logger.exception('Value error in processing the request', exc_info=True)
        return Response(f'Value error: {str(e)}', status=HTTPStatus.BAD_REQUEST)
    except Exception as e:
        logger.exception('Failed to process message', exc_info=True)
        return Response('Internal server error', status=HTTPStatus.INTERNAL_SERVER_ERROR)

if __name__ == '__main__':
    app.run(debug=False, port=3978, use_reloader=False)
