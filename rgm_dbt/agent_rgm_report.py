import os
import json
from dotenv import load_dotenv
from anthropic import Anthropic
from gold_metrics import get_gold_metrics

load_dotenv()
client = Anthropic()

tools = [
    {
        "name": "get_gold_metrics",
        "description": "Returns the governed gold-layer RGM metrics per SKU (price realization, ACV distribution and trend, promo penetration, promo lift, category share), which weeks they cover, and whether any week is incomplete. Always use this instead of estimating or recomputing numbers.",
        "input_schema": {"type": "object", "properties": {}}
    },
    {
        "name": "write_report",
        "description": "Writes the final RGM insights report to a markdown file.",
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
    print("\n--- CLAUDE WANTS TO WRITE THIS REPORT ---")
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
        "Get the gold RGM metrics. Then write an RGM insights report in markdown. "
        "State which weeks the metrics cover, and if incomplete_weeks is not empty, "
        "say which weeks are incomplete and that the figures reflect only the rows "
        "that passed data quality checks. For each SKU cover: price realization, "
        "ACV distribution and its trend, promo penetration, promo lift, and "
        "category share. Call out which SKU most needs a distribution push, which "
        "is getting the best return on promo spend, and give one recommendation per "
        "SKU. Rules: use the exact numbers from the tool and never recompute them; "
        "base every recommendation on the metrics themselves; do not invent causes, "
        "competitor context, or targets the data does not contain. Write the result "
        "to rgm_insights_report.md."
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
        print("\n[WARNING] The model hit the max_tokens limit before finishing.")
        print("Whatever it was building (likely the report or a tool call) is incomplete.")
        print("Raise max_tokens further, or ask for a shorter report, and try again.")
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

        if block.name == "get_gold_metrics":
            result = json.dumps(get_gold_metrics(), default=str)
        elif block.name == "write_report":
            result = write_report(**block.input)
        else:
            result = "Unknown tool."

        tool_results.append({"type": "tool_result", "tool_use_id": block.id, "content": result})

    messages.append({"role": "user", "content": tool_results})
