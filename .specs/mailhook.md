```
from dotenv import load_dotenv
load_dotenv()
import os
import json
from flask import Flask, request, Response
from agentmail import AgentMail
import logging

logging.basicConfig(
    format="%(levelname)s [%(asctime)s] %(name)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    level=logging.DEBUG
)


app = Flask(__name__)
agent_api_key = os.getenv("AGENTMAIL_API_KEY")
inbox_username = os.getenv("INBOX_USERNAME")
demo_target_email = os.getenv("DEMO_TARGET_EMAIL", "fallback.email@example.c
om")
inbox_client_id = "inbox-for-nanobot_dba_2026_03_06"
inbox_id = "nanobot_dba_2026_03_06@agentmail.to"

import httpx

client = AgentMail(
    api_key=agent_api_key,
    httpx_client=httpx.Client(
        transport=httpx.HTTPTransport(local_address="0.0.0.0"),
 #       headers={"Accept-Encoding": "*",
 #       'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:135.0)
Gecko/20100101 Firefox/135.0',
 #       'X-API-Key':agent_api_key}
    ),
)


class SimpleInbox:
    def __init__(self, inbox_id):
        self.inbox_id = inbox_id


inbox_id = f"{inbox_username}@agentmail.to"
inbox = client.inboxes.get(inbox_id=inbox_id)

@app.route("/webhook", methods=["POST"])
def receive_webhook():
    payload = request.get_json() if request.is_json else {}
    email_body = json.dumps(payload, indent=2)
    # email processing code here
    return Response(status=200)

if __name__ == "__main__":
    app.run(port=8080,debug=True)
```


```example email_body json
{
"body_included": true,
"event_id": "3ba9dea9-9b6d-4f8a-a2c1-353fd0d1b23a",
"event_type": "message.received",
"message": {
"created_at": "2026-03-21T20:53:44.512Z",
"extracted_html": "
1:53:pm
",
"extracted_text": "1:53:pm",
"from": "Dustin Andrews ",
"from_": "Dustin Andrews ",
"headers": {
"x-ms-exchange-messagesentrepresentingtype": "1"
},
"html": "\n\n\n\n\n\n
\n1:53:pm
\n\n\n",
"inbox_id": "summary@mailsummary.to",
"labels": [
"received",
"unread"
],
"message_id": "",
"organization_id": "dd68100c-7f19-4293-86fc-f91288dc75f6",
"pod_id": "dd68100c-7f19-4293-86fc-f91288dc75f6",
"preview": "1:53:pm\n",
"size": 9349,
"smtp_id": "5sdqarj2vjrrfqut1nv3cokt37s5jh13tkuat401",
"subject": "test 2",
"text": "1:53:pm\n",
"thread_id": "e610e035-cff2-43e0-a5b6-3e01f03104a9",
"timestamp": "2026-03-21T20:53:41.000Z",
"to": [
"summary@mailsummary.to"
],
"updated_at": "2026-03-21T20:53:44.512Z"
},
"thread": {
"created_at": "2026-03-21T20:53:44.512Z",
"inbox_id": "summary@mailsummary.to",
"labels": [
"received",
"unread"
],
"last_message_id": "",
"message_count": 1,
"organization_id": "dd68100c-7f19-4293-86fc-f91288dc75f6",
"pod_id": "dd68100c-7f19-4293-86fc-f91288dc75f6",
"preview": "1:53:pm\n",
"received_timestamp": "2026-03-21T20:53:41.000Z",
"recipients": [
"summary@mailsummary.to"
],
"senders": [
"Dustin Andrews "
],
"size": 9349,
"subject": "test 2",
"thread_id": "e610e035-cff2-43e0-a5b6-3e01f03104a9",
"timestamp": "2026-03-21T20:53:41.000Z",
"updated_at": "2026-03-21T20:53:44.512Z"
},
"type": "event"
}
```

This is our mailhook.
Todo:

- Make this a proper project that installs
- Change the /webhook path to capture "extracted_text" and call a configurable program with the text on SDTIN
E.G. if the program was grep it would be functionally identical to 
$ echo "this is the message text" | grep
