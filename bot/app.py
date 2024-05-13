# app.py
from __future__ import annotations

import logging
from http import HTTPStatus

from adapter import AdapterWithErrorHandler
from botbuilder.core import BotFrameworkAdapterSettings
from quart import jsonify
from quart import Quart
from quart import request
from quart import Response

from bot import scrumbag_bot  # Make sure this import doesn't trigger further imports that circle back
from shared.config import CLU_ENDPOINT
from shared.config import CLU_SECRET
from shared.config import MICROSOFT_APP_ID
from shared.config import MICROSOFT_APP_PASSWORD


logging.basicConfig(level=logging.INFO)

app = Quart(__name__)
SETTINGS = BotFrameworkAdapterSettings(MICROSOFT_APP_ID, MICROSOFT_APP_PASSWORD)
ADAPTER = AdapterWithErrorHandler(SETTINGS)
BOT = scrumbag_bot(SETTINGS)  # Pass SETTINGS or individual ID and PASSWORD

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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
    settings = {'endpoint': CLU_ENDPOINT, 'secret': CLU_SECRET}  # Example settings structure
    bot = scrumbag_bot(settings)
    app.run(debug=False, port=3978, use_reloader=False)
