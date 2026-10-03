import json
from dotenv import load_dotenv
from anthropic import Anthropic
from nl_query_tools import get_data_context, run_readonly_query

load_dotenv()
client = Anthropic()

SYSTEM = (
    "You answer business questions about CPG pet food retail performance using "
    "SQL against gold tables. Rules: (1) Call get_data_context before writing SQL "
    "so you know the columns, their definitions, and which weeks are complete. "
    "(2) Never do arithmetic yourself; get every number from a query result. "
    "(3) If the tables cannot answer the question, say so plainly instead of guessing. "
    "(4) If a comparison involves a week marked incomplete, say so in your answer. "
    "(5) Keep answers short: lead with the answer, then the key numbers."
)

tools = [
    {
        "name": "get_data_context",
        "description": "Returns the tables available, their columns and business definitions, and data coverage (which weeks have all SKUs present). Call this before writing SQL, and again whenever unsure what a column means or whether the data covers the question.",
        "input_schema": {"type": "object", "properties": {}}
    },
    {
        "name": "run_sql",
        "description": "Runs one read-only SELECT query (DuckDB SQL) against the tables described by get_data_context and returns up to 50 rows. Returns an error message if the query is invalid or not read-only; fix the query and try again.",
        "input_schema": {
            "type": "object",
            "properties": {"query": {"type": "string"}},
            "required": ["query"]
        }
    }
]

messages = []
print("Ask questions about the RGM data. Type 'quit' to exit.\n")

while True:
    question = input("Question: ").strip()
    if question.lower() in ("quit", "exit", ""):
        break

    checkpoint = len(messages)
    messages.append({"role": "user", "content": question})

    while True:
        response = client.messages.create(
            model="claude-sonnet-4-5",
            max_tokens=1500,
            system=SYSTEM,
            tools=tools,
            messages=messages
        )

        if response.stop_reason == "max_tokens":
            print("\n[WARNING] Hit max_tokens before finishing. Try a narrower question.\n")
            del messages[checkpoint:]   # roll back so the history stays valid
            break

        messages.append({"role": "assistant", "content": response.content})

        if response.stop_reason != "tool_use":
            print("\n" + response.content[0].text + "\n")
            break

        tool_results = []
        for block in response.content:
            if block.type != "tool_use":
                continue
            if block.name == "get_data_context":
                print("[Claude requested]: get_data_context")
                result = json.dumps(get_data_context(), default=str)
            elif block.name == "run_sql":
                print(f"[SQL run]: {block.input['query']}")
                result = json.dumps(run_readonly_query(block.input["query"]), default=str)
            else:
                result = "Unknown tool."
            tool_results.append({"type": "tool_result", "tool_use_id": block.id, "content": result})

        messages.append({"role": "user", "content": tool_results})
