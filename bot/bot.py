from slack import WebClient
from slack.errors import SlackApiError

from bot.credentials import Credentials

credentials = Credentials()


class Bot:
    def __init__(self):
        self.client = WebClient(token=credentials.bot_user_oAuth_access_token)

    def send_message(self, message):
        try:
            full_message = f'<@U01D9S0BXC2|cal>: {message}'
            response = self.client.chat_postMessage(
                channel='#bot-things',
                text=full_message,
                )
            assert response["message"]["text"] == full_message
        except SlackApiError as e:
            # You will get a SlackApiError if "ok" is False
            assert e.response["ok"] is False
            assert e.response["error"]  # str like 'invalid_auth', 'channel_not_found'
            print(f"Got an error: {e.response['error']}")
            raise e
