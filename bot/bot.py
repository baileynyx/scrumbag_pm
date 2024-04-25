from __future__ import annotations

import logging

from botbuilder.core import ActivityHandler
from botbuilder.core import MessageFactory
from botbuilder.core import TurnContext

# Configure logger for EchoBot
logger = logging.getLogger(__name__)
# Ensure the logger is set to a level that will capture all info logs
logger.setLevel(logging.INFO)


class EchoBot(ActivityHandler):
    async def on_message_activity(self, turn_context: TurnContext):
        # Log the receipt of the message
        logger.info(f"Received message: {turn_context.activity.text}")

        # Attempt to echo the message back to the user
        try:
            await turn_context.send_activity(MessageFactory.text(turn_context.activity.text))
            logger.info(f"Echoed back message: {turn_context.activity.text}")
        except Exception as e:
            logger.error(f"Error sending activity: {str(e)}", exc_info=True)
