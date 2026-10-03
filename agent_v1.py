import os
from dotenv import load_dotenv
from anthropic import Anthropic

load_dotenv()
client = Anthropic()

# This describes a tool to Claude: a name, what it does, and what
# input it needs. Claude never runs this itself, it only asks us to.
tools = [
    {
        "name": "read_notes_file",
        "description": "Reads a meeting notes text file from disk.",
        "input_schema": {
            "type": "object",
            "properties": {
                "filename": {"type": "string", "description": "Name of the file to read"}
            },
            "required": ["filename"]
        }
    }
]

def read_notes_file(filename):
    with open(filename, "r") as f:
        return f.read()

messages = [
    {"role": "user", "content": "Read notes.txt and extract action items: task, owner, deadline."}
]

response = client.messages.create(
    model="claude-sonnet-4-5",
    max_tokens=500,
    tools=tools,
    messages=messages
)

# stop_reason tells us why Claude stopped talking. "tool_use" means
# it wants to call one of our tools before it can finish the job.
if response.stop_reason == "tool_use":
    tool_call = next(b for b in response.content if b.type == "tool_use")
    print(f"[Claude requested]: {tool_call.name}(filename='{tool_call.input['filename']}')")

    # WE run the actual function. Claude only ever asks, never executes.
    result = read_notes_file(tool_call.input["filename"])

    # Hand the file contents back so Claude can finish the task.
    messages.append({"role": "assistant", "content": response.content})
    messages.append({
        "role": "user",
        "content": [{"type": "tool_result", "tool_use_id": tool_call.id, "content": result}]
    })

    final = client.messages.create(
        model="claude-sonnet-4-5",
        max_tokens=500,
        tools=tools,
        messages=messages
    )
    print("\n" + final.content[0].text)
else:
    print(response.content[0].text)
