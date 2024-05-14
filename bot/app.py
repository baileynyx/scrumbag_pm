from __future__ import annotations

import logging
from http import HTTPStatus

from adapter import AdapterWithErrorHandler
from botbuilder.core import BotFrameworkAdapter
from botbuilder.core import BotFrameworkAdapterSettings
from botbuilder.schema import Activity
from quart import jsonify
from quart import Quart
from quart import request
from quart import Response

from bot import ScrumBagBot  # Ensure this import doesn't trigger further imports that circle back
from shared.config import CLU_ENDPOINT
from shared.config import CLU_SECRET
from shared.config import MICROSOFT_APP_ID
from shared.config import MICROSOFT_APP_PASSWORD
# Importing configurations securely from shared configurations

# Setup basic logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Quart(__name__)
SETTINGS = BotFrameworkAdapterSettings(MICROSOFT_APP_ID, MICROSOFT_APP_PASSWORD)
ADAPTER = AdapterWithErrorHandler(SETTINGS)

@app.route('/api/messages', methods=['POST'])
async def messages():
    if 'application/json' not in request.headers.get('Content-Type', ''):
        logger.error('Received non-JSON content type')
        return Response('Unsupported media type', status=HTTPStatus.UNSUPPORTED_MEDIA_TYPE)

    try:
        body = await request.get_json()
        logger.info(f"Processing message with body: {body}")

        # Deserialize the activity sent from the Bot Framework or the Emulator
        activity = Activity().deserialize(body)
        auth_header = request.headers.get('Authorization', '')

        # Process the activity with the bot's logic
        await ADAPTER.process_activity(activity, auth_header, ScrumBagBot.on_turn)
        return Response('Handled', status=HTTPStatus.OK)

    except Exception as e:
        logger.exception('Failed to process message', exc_info=True)
        return Response('Internal server error', status=HTTPStatus.INTERNAL_SERVER_ERROR)

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=3978, use_reloader=False)
