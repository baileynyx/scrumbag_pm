from __future__ import annotations

import logging

from botbuilder.core import BotFrameworkAdapter
from botbuilder.core import BotFrameworkAdapterSettings
from botbuilder.core import TurnContext
from botbuilder.schema import Activity
from botbuilder.schema import ConversationReference

# Configure logging
logger = logging.getLogger(__name__)


class AdapterWithErrorHandler(BotFrameworkAdapter):
    def __init__(self, settings: BotFrameworkAdapterSettings):
        super().__init__(settings)
        # Catch-all for errors in the adapter process
        self.on_turn_error = self.handle_turn_error

    async def handle_turn_error(self, turn_context: TurnContext, error: Exception):
        # Log any errors that happen during the turn
        logger.error(f"Unhandled exception: {error}", exc_info=True)

        # Send a message to the user
        await turn_context.send_activity('Sorry, it looks like something went wrong.')

        # Clear out state
        await self.clear_state(turn_context)

    async def clear_state(self, turn_context: TurnContext):
        try:
            # Delete the conversation state for the current context
            await turn_context.adapter.conversation_state.delete(turn_context)
        except Exception as e:
            logger.exception(
                'Exception occurred when trying to clear conversation state.', exc_info=True,
            )

    # Optionally, override other methods to add more specific logging
    async def send_activities(self, context: TurnContext, activities: list[Activity]):
        # Log activities being sent
        for activity in activities:
            if activity.type == 'message':
                logger.info(f"Sending message: {activity.text}")
        return await super().send_activities(context, activities)

    async def continue_conversation(self, reference: ConversationReference, callback, bot_id: str = None):
        logger.info(f"Continuing conversation with reference: {
                    reference.conversation.id
        }")
        return await super().continue_conversation(reference, callback, bot_id=bot_id)
