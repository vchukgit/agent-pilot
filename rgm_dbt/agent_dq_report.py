import os
import json
from dotenv import load_dotenv
from anthropic import Anthropic
from dq_check import get_dq_summary

load_dotenv()
client = Anthropic()

tools = [
    {
        "name": "get_dq_summary",
        "description": "Returns the current data quality state: total staged rows, total clean rows, and details of every dbt test failure with sample offending rows. Always use this instead of guessing at data quality.",
        "input_schema": {"type": "object", "properties": {}}
    },
    {
        "name": "write_report",
        "description": "Writes the final data quality report to a markdown file.",
        "input_schema": {
            "type": "object",
            "properties": {
                "filename": {"type": "string"},
                "content": {"type": "string"}
            },
            "required": ["filename", "content"]
        }
    }
]

def write_report(filename, content):
    print("\n--- CLAUDE WANTS TO WRITE THIS DQ REPORT ---")
    print(f"File: {filename}\n")
    print(content)
    print("--- END OF PROPOSED REPORT ---")
    answer = input("\nApprove writing this file? (y/n): ").strip().lower()
    if answer == "y":
        with open(filename, "w") as f:
            f.write(content)
        return "File written successfully."
    else:
        return "User declined. Do not write the file."

messages = [
    {"role": "user", "content": (
        "Get the current data quality summary. Then write a DQ report in markdown "
        "for a data steward. Cover: overall health (rows staged vs. rows that made "
        "it into the clean dataset), and for each failing test, explain in plain "
        "language what went wrong and give an explicit recommendation, either "
        "'safe to auto-resolve' (like an exact duplicate resend, already handled "
        "automatically) or 'must stay quarantined pending investigation' (an "
        "impossible or corrupted value that cannot be safely guessed at). Use the "
        "exact numbers and rows from the tool, do not estimate. Write the result "
        "to dq_report.md."
    )}
]

while True:
    response = client.messages.create(
        model="claude-sonnet-4-5",
        max_tokens=2000,
        tools=tools,
        messages=messages
    )

    if response.stop_reason == "max_tokens":
        print("\n[WARNING] Hit max_tokens before finishing. Raise the limit and retry.")
        break

    if response.stop_reason != "tool_use":
        print("\n" + response.content[0].text)
        break

    messages.append({"role": "assistant", "content": response.content})

    tool_results = []
    for block in response.content:
        if block.type != "tool_use":
            continue
        print(f"[Claude requested]: {block.name}({block.input})")

        if block.name == "get_dq_summary":
            result = json.dumps(get_dq_summary())
        elif block.name == "write_report":
            result = write_report(**block.input)
        else:
            result = "Unknown tool."

        tool_results.append({"type": "tool_result", "tool_use_id": block.id, "content": result})

    messages.append({"role": "user", "content": tool_results})
