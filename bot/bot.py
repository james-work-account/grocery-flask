from slack import WebClient
from slack.errors import SlackApiError


class Bot:
    def __init__(self):
        try:
            from bot.credentials import Credentials
            credentials = Credentials()
            self.client = WebClient(token=credentials.bot_user_oAuth_access_token)
        except ImportError:
            pass

    def send_message_with_tag(self, message, e):
        self.send_message(f'<@U01D9S0BXC2|cal>: {message}', e)

    def send_message(self, message, e):
        try:
            self.client.chat_postMessage(
                channel='#bot-things',
                text=message + '\n' + repr(e),
            )
        except SlackApiError as e:
            # You will get a SlackApiError if "ok" is False
            assert e.response["ok"] is False
            assert e.response["error"]  # str like 'invalid_auth', 'channel_not_found'
            print(f"Got an error: {e.response['error']}")
            raise e
        except AttributeError:
            pass