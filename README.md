  Federal Register RAG Agent (Take-Home Assessment)

This is a user-facing RAG (Retrieval-Augmented Generation) system powered by a local LLM using [Ollama](https://ollama.com/), designed to answer questions about U.S. federal documents by interacting with a MySQL-backed data pipeline.

---

  Features

- Async data pipeline to fetch daily federal documents from the [Federal Register API](https://www.federalregister.gov/developers/documentation/api/v1)
- MySQL database to store and retrieve records
- LLM-powered agent (via Ollama with Qwen 0.5b) that:
  - Parses user questions
  - Calls a tool function to fetch documents
  - Optionally summarizes them
- Streamlit web UI for interactive chat
- Fallback logic for keyword and time-based queries (e.g. “from last week”)

---

  Setup Instructions

 1. Clone the repository and navigate to the folder

```bash
git clone <your_repo_url>
cd rag_agent_project
```

 2. Create virtual environment and activate it

```bash
python -m venv venv
venv\Scripts\activate      On Windows
 source venv/bin/activate   On macOS/Linux
```

 3. Install required Python packages

```bash
pip install -r requirements.txt
```

 4. Install and run Ollama

Install from https://ollama.com and then pull the model:

```bash
ollama pull qwen:0.5b
ollama run qwen:0.5b
```

Leave the Ollama terminal open while running the app.

 5. Create `.env` file

```dotenv
DB_HOST=localhost
DB_USER=your_mysql_user
DB_PASSWORD=your_mysql_password
DB_NAME=federal_register
```

 6. Run the data pipeline to populate the database

```bash
python data_pipeline.py
```

 7. Launch the Streamlit UI

```bash
streamlit run app.py
```

---

  Example Queries to Try

- Show documents about environment  
- Find public safety notices from last week  
- Get federal documents about cybersecurity  
- Executive orders by Joe Biden  
- Documents on education reform

---

  Project Structure

```
rag_agent_project/
│
├── app.py                 Streamlit UI
├── agent.py               Agent logic with tool + fallback
├── tools.py               Tool functions for database interaction
├── data_pipeline.py       Fetch + store data from API
├── requirements.txt
├── .env
└── README.md
```

---

  Notes

- Only raw SQL is used — no ORM
- The LLM cannot call external APIs — it only uses your database
- VectorDB is **not used**, per task requirement
