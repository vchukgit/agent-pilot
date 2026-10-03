import os
from dotenv import load_dotenv
from anthropic import Anthropic

load_dotenv()  # reads the .env file and loads ANTHROPIC_API_KEY

client = Anthropic()  # automatically picks up the key from the environment

response = client.messages.create(
    model="claude-sonnet-4-5",
    max_tokens=200,
    messages=[
        {"role": "user", "content": "Say hello in one sentence, and tell me what model you are."}
    ]
)

print(response.content[0].text)
