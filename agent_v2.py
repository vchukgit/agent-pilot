import os
from dotenv import load_dotenv
from anthropic import Anthropic

load_dotenv()
client = Anthropic()

tools = [
    {
        "name": "read_notes_file",
        "description": "Reads a meeting notes text file from disk.",
        "input_schema": {
            "type": "object",
            "properties": {"filename": {"type": "string"}},
            "required": ["filename"]
        }
    },
    {
        "name": "write_summary_file",
        "description": "Writes the final action items summary to a markdown file on disk.",
        "input_schema": {
            "type": "object",
            "properties": {
                "filename": {"type": "string"},
                "content": {"type": "string", "description": "The full markdown content to write"}
            },
            "required": ["filename", "content"]
        }
    }
]

def read_notes_file(filename):
    with open(filename, "r") as f:
        return f.read()

def write_summary_file(filename, content):
    print("\n--- CLAUDE WANTS TO WRITE THIS FILE ---")
    print(f"File: {filename}\n")
    print(content)
    print("--- END OF PROPOSED CONTENT ---")
    answer = input("\nApprove writing this file? (y/n): ").strip().lower()
    if answer == "y":
        with open(filename, "w") as f:
            f.write(content)
        return "File written successfully."
    else:
        return "User declined. Do not write the file."

messages = [
    {"role": "user", "content": "Read notes.txt, extract action items as a markdown table, then write the result to action_items.md."}
]

while True:
    response = client.messages.create(
        model="claude-sonnet-4-5",
        max_tokens=800,
        tools=tools,
        messages=messages
    )

    if response.stop_reason != "tool_use":
        print("\n" + response.content[0].text)
        break

    messages.append({"role": "assistant", "content": response.content})

    tool_results = []
    for block in response.content:
        if block.type != "tool_use":
            continue
        print(f"[Claude requested]: {block.name}({block.input})")

        if block.name == "read_notes_file":
            result = read_notes_file(**block.input)
        elif block.name == "write_summary_file":
            result = write_summary_file(**block.input)
        else:
            result = "Unknown tool."

        tool_results.append({"type": "tool_result", "tool_use_id": block.id, "content": result})

    messages.append({"role": "user", "content": tool_results})
