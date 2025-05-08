import asyncio
from agent import run_agent

query = "Call fetch_documents_by_keyword to get recent documents about cybersecurity"
response = asyncio.run(run_agent(query))
print(response)
