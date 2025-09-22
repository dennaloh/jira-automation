from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

SLACK_BOT_TOKEN = ""
SLACK_APP_TOKEN = ""

REQUEST_KEYWORDS = [
    "private cloud",
    "athens",
    "ares",
    "onprem",
    "on premises",
    "credentials"
]

app = App(token=SLACK_BOT_TOKEN)

@app.event("message")
def handle_message_events(body, client):
    try:
        msg = body['event'].get('text', '')
        if msg and ("access" in msg.lower()) and any(keyword in msg.lower() for keyword in REQUEST_KEYWORDS):
            channel_id = body['event']['channel']
            user_id = body['event']['user']
            thread_ts = body['event']['ts']  # timestamp of the original message
            client.chat_postMessage(
                channel=channel_id,
                text=f"<@{user_id}> It seems you have a request related to our services.",
                thread_ts=thread_ts  # replies in the same thread
            )
    except Exception as e:
        print(f"Error processing message: {e}")
        print(body['event'])

if __name__ == "__main__":
    SocketModeHandler(app, SLACK_APP_TOKEN).start()