import os
from dotenv import load_dotenv
from anthropic import Anthropic

load_dotenv()
client = Anthropic()

tools = [
    {
        "name": "read_sample_data",
        "description": "Reads a sample data file (CSV) so its columns and values can be inspected to infer a schema.",
        "input_schema": {
            "type": "object",
            "properties": {"filename": {"type": "string"}},
            "required": ["filename"]
        }
    },
    {
        "name": "write_ingestion_config",
        "description": "Writes a YAML ingestion config describing the source name, inferred columns with data types, and a candidate primary key. Explicitly flag any row values that do not fit the inferred type for their column, any nulls or blanks, and any values outside the typical range for that column.",
        "input_schema": {
            "type": "object",
            "properties": {
                "filename": {"type": "string"},
                "content": {"type": "string", "description": "The full YAML content to write"}
            },
            "required": ["filename", "content"]
        }
    }
]

def read_sample_data(filename):
    with open(filename, "r") as f:
        return f.read()

def write_ingestion_config(filename, content):
    print("\n--- CLAUDE WANTS TO WRITE THIS INGESTION CONFIG ---")
    print(f"File: {filename}\n")
    print(content)
    print("--- END OF PROPOSED CONFIG ---")
    answer = input("\nApprove writing this file? (y/n): ").strip().lower()
    if answer == "y":
        with open(filename, "w") as f:
            f.write(content)
        return "File written successfully."
    else:
        return "User declined. Do not write the file."

messages = [
    {"role": "user", "content": (
        "Read sample_data.csv. Infer a schema: column names, a likely data type for "
        "each (string, integer, float, date, boolean), and a candidate primary key. Explicitly flag any row values that do not fit the inferred type for their column, any nulls or blanks, and any values outside the typical range for that column. "
        "Then draft a YAML ingestion config with fields: source_name, columns (name "
        "and type for each), and primary_key. Write it to ingestion_config.yaml."
    )}
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

        if block.name == "read_sample_data":
            result = read_sample_data(**block.input)
        elif block.name == "write_ingestion_config":
            result = write_ingestion_config(**block.input)
        else:
            result = "Unknown tool."

        tool_results.append({"type": "tool_result", "tool_use_id": block.id, "content": result})

    messages.append({"role": "user", "content": tool_results})
