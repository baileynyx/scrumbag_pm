from __future__ import annotations

import os
import sys
from pathlib import Path

root_dir = Path(__file__).resolve().parent.parent
sys.path.append(str(root_dir))

# Import configurations directly to avoid circular imports
from shared.config import CLU_ENDPOINT, CLU_SECRET, CLU_PROJECT_NAME
from shared.utils import log_message, log_debug_info

import logging
from botbuilder.core import ActivityHandler, MessageFactory, TurnContext
import requests  # Import requests to make HTTP calls to the CLU service

# Configure logger for EnhancedBot using the shared utility logger
logger = logging.getLogger('EnhancedBotLogger')

# Function to query the CLU service
async def query_clu(text: str):
    endpoint_url = CLU_ENDPOINT  # Use the endpoint from the config
    headers = {
        'Content-Type': 'application/json',
        'Ocp-Apim-Subscription-Key': CLU_SECRET  # Use the secret from the config
    }
    body = {
        'query': text,
        'projectName': CLU_PROJECT_NAME,  # Use the CLU project name from the config
        'deploymentName': 'production'
    }
    log_debug_info('Sending request to CLU', endpoint=endpoint_url, project_name=CLU_PROJECT_NAME)
    response = requests.post(endpoint_url, json=body, headers=headers)
    log_message('info', f"Received CLU response: {response.json()}")
    return response.json()

class scrumbag_bot(ActivityHandler):
    async def on_message_activity(self, turn_context: TurnContext):
        user_message = turn_context.activity.text
        log_message('info', f"Received message: {user_message}")

        # Query CLU with the user message
        clu_response = await query_clu(user_message)
        log_message('info', f"CLU Response: {clu_response}")

        # Handle different intents based on the CLU response
        intent = clu_response.get('prediction', {}).get('topIntent', {}).get('intent', 'None')
        log_message('debug', f"Handling intent: {intent}")

        if intent == 'Greeting':
            response_text = 'Hello there! How can I assist you today?'
        elif intent == 'Help':
            response_text = 'Sure! What do you need help with?'
        else:
            response_text = "I'm here to help, but I didn't quite understand that."

        try:
            await turn_context.send_activity(MessageFactory.text(response_text))
            log_message('info', f"Sent response: {response_text}")
        except Exception as e:
            log_message('error', f"Error sending activity: {str(e)}", exc_info=True)

if __name__ == '__main__':
    app.run(debug=False, port=3978, use_reloader=False)
