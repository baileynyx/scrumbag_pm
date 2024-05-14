from __future__ import annotations

import logging

from botbuilder.core import BotFrameworkAdapter
from botbuilder.core import TurnContext
from botbuilder.schema import Activity
from botbuilder.schema import ConversationReference

# Configure logger for adapter-related operations
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)

class AdapterWithErrorHandler(BotFrameworkAdapter):
    """
    Custom adapter class for the Bot Framework that includes error handling.
    """

    def __init__(self, settings):
        super().__init__(settings)
        # Catch-all for errors in the adapter process
        self.on_turn_error = self.handle_turn_error

    async def handle_turn_error(self, turn_context: TurnContext, error: Exception):
        """
        Handles any uncaught exceptions during the turn processing.
        """
        logger.error(f"Unhandled exception: {error}", exc_info=True)

        # Send a message to the user
        await turn_context.send_activity('Sorry, it looks like something went wrong.')

        # Clear out state
        await self.clear_state(turn_context)

    async def clear_state(self, turn_context: TurnContext):
        """
        Clears the conversation state.
        """
        try:
            await turn_context.adapter.conversation_state.delete(turn_context)
        except Exception as e:
            logger.exception('Exception occurred when trying to clear state.', exc_info=True)

    async def send_activities(self, context: TurnContext, activities: list[Activity]):
        """
        Override the send_activities method to add custom logging.
        """
        for activity in activities:
            if activity.type == 'message':
                logger.info(f"Sending message: {activity.text}")
        return await super().send_activities(context, activities)

    async def continue_conversation(self, reference: ConversationReference, callback, bot_id: str = None):
        """
        Continues a conversation using a reference.
        """
        logger.info(f"Continuing conversation with reference: {reference.conversation.id}")
        return await super().continue_conversation(reference, callback, bot_id=bot_id)
