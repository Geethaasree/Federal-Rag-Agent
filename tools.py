import aiomysql
import os
from dotenv import load_dotenv

load_dotenv()

async def fetch_documents_by_keyword(keyword: str, from_date: str = None, to_date: str = None):
    query = "SELECT title, publication_date, document_type, html_url FROM documents WHERE title LIKE %s"
    params = [f"%{keyword}%"]

    if from_date and to_date:
        query += " AND publication_date BETWEEN %s AND %s"
        params += [from_date, to_date]

    pool = await aiomysql.create_pool(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        db=os.getenv("DB_NAME"),
        autocommit=True
    )
    async with pool.acquire() as conn:
        async with conn.cursor(aiomysql.DictCursor) as cur:
            await cur.execute("""
                SELECT title, publication_date, document_type, html_url
                FROM documents
                WHERE title LIKE %s
                ORDER BY publication_date DESC
                LIMIT 5
            """, (f"%{keyword}%",))
            results = await cur.fetchall()
    pool.close()
    await pool.wait_closed()
    return results
