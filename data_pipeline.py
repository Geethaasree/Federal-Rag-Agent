import asyncio
import aiohttp
import aiomysql
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

DB_HOST = os.getenv("DB_HOST")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME")

async def fetch_documents(session, start_date, end_date, page=1):
    url = "https://www.federalregister.gov/api/v1/documents.json"
    params = {
        "per_page": 100,
        "page": page,
        "order": "newest",
        "conditions[publication_date][gte]": start_date,
        "conditions[publication_date][lte]": end_date
    }
    async with session.get(url, params=params) as response:
        return await response.json()

async def save_documents(pool, documents):
    async with pool.acquire() as conn:
        async with conn.cursor() as cur:
            for doc in documents:
                try:
                    await cur.execute("""
    INSERT INTO documents (document_number, title, publication_date, document_type, html_url, pdf_url, json_url)
    VALUES (%s, %s, %s, %s, %s, %s, %s) AS new
    ON DUPLICATE KEY UPDATE
        title = new.title,
        publication_date = new.publication_date,
        document_type = new.document_type,
        html_url = new.html_url,
        pdf_url = new.pdf_url,
        json_url = new.json_url
""", 
 (
                        doc.get("document_number"),
                        doc.get("title"),
                        doc.get("publication_date"),
                        doc.get("type"),
                        doc.get("html_url"),
                        doc.get("pdf_url"),
                        doc.get("json_url")
                    ))
                    await conn.commit()
                except Exception as e:
                    print(f"Error saving document {doc.get('document_number')}: {e}")

async def main():
    start_date = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
    end_date = datetime.now().strftime("%Y-%m-%d")
    async with aiohttp.ClientSession() as session:
        page = 1
        while True:
            data = await fetch_documents(session, start_date, end_date, page)
            documents = data.get("results", [])
            if not documents:
                break
            pool = await aiomysql.create_pool(
                host=DB_HOST,
                user=DB_USER,
                password=DB_PASSWORD,
                db=DB_NAME,
                autocommit=True
            )
            await save_documents(pool, documents)
            pool.close()
            await pool.wait_closed()
            page += 1

if __name__ == "__main__":
    asyncio.run(main())
