from __future__ import annotations

import logging
import sys
from pathlib import Path

from botbuilder.core import ActivityHandler
from botbuilder.core import MessageFactory
from botbuilder.core import TurnContext

# Adjust the path to include the root directory of the project
root_dir = Path(__file__).resolve().parent.parent
sys.path.append(str(root_dir))

from shared.config import CLU_ENDPOINT, CLU_SECRET, MICROSOFT_APP_ID
from shared.utils import log_message, log_debug_info
import requests  # Used for making HTTP calls

# Configure logger
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

class ScrumBagBot(ActivityHandler):
    """
    Bot handler class for processing user messages.
    """

    async def on_message_activity(self, turn_context: TurnContext):
        """
        Handles message activities from users.
        """
        user_message = turn_context.activity.text
        log_message('info', f"Received message: {user_message}")

        # Process the message and query CLU with the user's message
        response = await self.query_clu(user_message)
        intent = response.get('topIntent', {}).get('intent', 'None')

        if intent == 'Greeting':
            response_text = 'Hello there! How can I assist you today?'
        elif intent == 'Help':
            response_text = 'Sure! What do you need help with?'
        else:
            response_text = "I'm here to help, but I didn't quite understand that."

        # Send a reply to the user
        await turn_context.send_activity(MessageFactory.text(response_text))
        log_message('info', f"Sent response: {response_text}")

    async def query_clu(self, text: str):
        """
        Query the CLU service with the provided text and return the response.
        """
        endpoint_url = f"{CLU_ENDPOINT}/analyze"
        headers = {
            'Content-Type': 'application/json',
            'Ocp-Apim-Subscription-Key': CLU_SECRET
        }
        body = {
            'query': text,
            'projectName': MICROSOFT_APP_ID,
            'deploymentName': 'production'
        }
        response = requests.post(endpoint_url, json=body, headers=headers)
        if response.status_code == 200:
            return response.json()
        else:
            logger.error(f"Failed to query CLU: {response.text}")
            return {}

if __name__ == '__main__':
    from quart import Quart, request

    app = Quart(__name__)

    @app.route('/api/messages', methods=['POST'])
    async def messages():
        """
        Main endpoint for processing messages from users.
        """
        if 'application/json' not in request.headers.get('Content-Type', ''):
            return Response('Unsupported Media Type', HTTPStatus.UNSUPPORTED_MEDIA_TYPE)

        body = await request.get_json()
        activity = Activity.deserialize(body)
        adapter = BotFrameworkAdapter(settings)
        turn_context = TurnContext(adapter, activity)

        bot = ScrumBagBot()
        await bot.on_turn(turn_context)

        return 'Message processed', HTTPStatus.OK

    app.run(debug=False, port=3978, use_reloader=False)
