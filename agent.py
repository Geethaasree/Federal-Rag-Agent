# agent.py
import json
import re
from datetime import datetime, timedelta
from tools import fetch_documents_by_keyword
import ollama

async def run_agent(user_query: str):
        # Friendly response for casual greetings
    if any(greet in user_query.lower() for greet in ["how are you", "hi", "hello", "what's up", "who are you", "hey"]):
        return "😊 I'm just a helpful AI agent ready to assist you with U.S. federal documents! Ask me things like:\n- Show documents about AI\n- Find public safety notices from last week"

    messages = [
        {
            "role": "system",
            "content": (
                "You are an AI agent that can call tools to retrieve government data.\n"
                "If a tool is needed, reply ONLY with a valid JSON block in this format, with no extra text:\n\n"
                '{\n'
                '  "function": "fetch_documents_by_keyword",\n'
                '  "args": {\n'
                '    "keyword": "artificial intelligence"\n'
                '  }\n'
                '}\n\n'
                "Do NOT include explanations, nested functions, or JavaScript-like syntax. Only respond with this JSON structure."
            )
        },
        {"role": "user", "content": user_query}
    ]

    print("👉 Sending user query to LLM...")
    response = ollama.chat(model="qwen:0.5b", messages=messages)
    content = response["message"]["content"]
    print("🧠 LLM Response:\n", content)

    try:
        # Try to extract JSON tool call
        json_block_match = re.search(r'\{[\s\S]*?"function"\s*:\s*".+?",\s*"args"\s*:\s*\{[\s\S]*?\}\s*\}', content)
        if json_block_match:
            json_str = json_block_match.group(0)
            json_data = json.loads(json_str)
            print("📦 Parsed Tool Call JSON:", json_data)

            function_name = json_data.get("function") or json_data.get("func")
            if function_name == "fetch_documents_by_keyword":
                args = json_data.get("args", {})
                result = await fetch_documents_by_keyword(**args)

                if not result:
                    return f"❌ No documents found for '{args.get('keyword')}'. Try a broader keyword like 'environment', 'security', or 'policy'."

                doc_list = "\n\n".join([
                    f"📄 {doc['title']} ({doc['publication_date']})\n"
                    f"Type: {doc['document_type']}\n"
                    f"Link: {doc['html_url']}"
                    for doc in result
                ])
                return "📄 Top Documents:\n\n" + doc_list

        # Fallback: extract keyword and optional week filter
        keyword_match = re.search(
            r"(?:about|on|related to|find|show documents about)\s+([a-zA-Z\s]+?)(?:\s+from\s+(this|last)\s+week)?",
            user_query.lower()
        )

        if keyword_match:
            keyword = keyword_match.group(1).strip()
            week_range = keyword_match.group(2)
            print("⚠️ Fallback keyword used:", keyword)

            today = datetime.today().date()
            from_date = None
            to_date = None

            if week_range == "last":
                from_date = today - timedelta(days=14)
                to_date = today - timedelta(days=7)
            elif week_range == "this":
                from_date = today - timedelta(days=7)
                to_date = today

            result = await fetch_documents_by_keyword(
                keyword=keyword,
                from_date=from_date.isoformat() if from_date else None,
                to_date=to_date.isoformat() if to_date else None
            )

            if not result:
                return f"❌ No documents found for '{keyword}'. Try something else like 'AI', 'finance', or 'policy'."

            doc_list = "\n\n".join([
                f"📄 {doc['title']} ({doc['publication_date']})\n"
                f"Type: {doc['document_type']}\n"
                f"Link: {doc['html_url']}"
                for doc in result
            ])
            return f"📄 Top Documents (fallback for '{keyword}'):\n\n" + doc_list

        return "⚠️ Sorry, I couldn't extract a valid function call. Please try rephrasing your question."

    except json.JSONDecodeError as e:
        print("❌ JSON Decode Error:", e)
        return "Sorry, the AI returned malformed data. Try again."
