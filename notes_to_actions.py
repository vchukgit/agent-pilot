import os
from dotenv import load_dotenv
from anthropic import Anthropic

load_dotenv()
client = Anthropic()

meeting_notes = """
Team sync, Sept 17.
Sarah will send the BMO proposal draft by Friday.
We need to decide on the Q4 pricing before the client call next week, Venu to own that.
Design team is blocked on the logo assets, someone needs to follow up with the vendor.
Next meeting moved to Tuesday 10am.
"""

response = client.messages.create(
    model="claude-sonnet-4-5",
    max_tokens=500,
    system="You extract clear action items from meeting notes. For each one, list: the task, who owns it, and the deadline if one is mentioned. Format as a simple numbered list. If no owner or deadline is stated, say 'unspecified'.",
    messages=[
        {"role": "user", "content": meeting_notes}
    ]
)

print(response.content[0].text)
