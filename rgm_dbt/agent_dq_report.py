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
        "description": "Returns the current data quality state: how many week and SKU combinations are loaded and how many have a clean row, every excluded row with the reason and whether it was resolved, anything needing attention, and details of any failing dbt tests. Always use this instead of guessing at data quality.",
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
        "Get the current data quality summary. Then write a short DQ report in "
        "markdown for a data steward. Rules: base every statement on the tool "
        "output; do not speculate about causes the tool does not state; do not "
        "invent thresholds, policies, or contacts; do not compute a pass rate "
        "from staged versus clean row counts, because staged includes old "
        "versions that later batches replaced, so use current_state instead. "
        "Cover: (1) current state: how many week and SKU combinations are loaded "
        "and how many have a clean row; (2) each excluded row group, saying why "
        "it was excluded and how it was resolved, in plain language; (3) a "
        "separate section for anything in exclusions_needing_attention, with a "
        "specific recommended action; if that list is empty, say plainly that "
        "nothing needs attention; (4) any failing tests, with the offending rows. "
        "Use the exact numbers from the tool. Write the result to dq_report.md."
    )}
]

while True:
    response = client.messages.create(
        model="claude-sonnet-4-5",
        max_tokens=3000,
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
            result = json.dumps(get_dq_summary(), default=str)
        elif block.name == "write_report":
            result = write_report(**block.input)
        else:
            result = "Unknown tool."

        tool_results.append({"type": "tool_result", "tool_use_id": block.id, "content": result})

    messages.append({"role": "user", "content": tool_results})
