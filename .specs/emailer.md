emailer

```sample code
from dotenv import load_dotenv
load_dotenv()
import os
import json
from agentmail import AgentMail
import logging

agent_api_key = os.getenv("AGENTMAIL_API_KEY")
inbox_username = os.getenv("INBOX_USERNAME")
demo_target_email = os.getenv("DEMO_TARGET_EMAIL", "fallback.email@example.com")
inbox_client_id = "inbox-for-nanobot_dba_2026_03_06"
inbox_id = "nanobot_dba_2026_03_06@agentmail.to"

try:

    client.inboxes.messages.send(
    inbox_id=inbox.inbox_id,
    to=[demo_target_email],
    subject="Hello from AgentMail!",
    html="<p>This is an <strong>HTML</strong> message.</p>"
    )

except Exception as e:
    print(f"Failed to send email: {e}")
```

- program will accept input on stdin
- parse the first line for the recipient address
- send the rest of the text as an html message to the address using agentmail