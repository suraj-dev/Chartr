from dotenv import load_dotenv
load_dotenv()
import openai
import os
from src.db import get_connection

openai_api_key = os.getenv("OPENAI_KEY")
openai_api_base = os.getenv("LLM_HOST")
client = None
schema_str = None
def get_openai_client() -> openai.OpenAI:
    global client
    if client is None:
        client = openai.OpenAI(api_key=openai_api_key, base_url=openai_api_base)
    return client

def nl_to_sql(query: str):
    prompt = build_prompt(query)
    client = get_openai_client()
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7
    )
    if response.choices is not None:
        return response.choices[0].message.content
    else:
        print("No response from LLM model")

def extract_db_schema() -> str:
    global schema_str
    if schema_str is None:
        connection = get_connection()
        cursor = connection.cursor()
        # Get all table names (you can filter for a specific schema if needed)
        cursor.execute("""
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = 'public'
            AND table_type = 'BASE TABLE'
        """)
        tables = [row[0] for row in cursor.fetchall()]

        schema_str = ""
        for table in tables:
            cursor.execute(f"""
                SELECT column_name, data_type
                FROM information_schema.columns
                WHERE table_name = %s
                ORDER BY ordinal_position
            """, (table,))
            columns = cursor.fetchall()
            schema_str += f"Table '{table}':\n"
            for col_name, data_type in columns:
                schema_str += f"  - {col_name}: {data_type}\n"
            schema_str += "\n"
    return schema_str

def build_prompt(nl_query):
    schema_description = extract_db_schema()
    return (
        f"You are an SQL expert. The database has the following tables and columns:\n"
        f"{schema_description}\n"
        f"Convert the following natural language query into an SQL query: '{nl_query}'. Return only the SQL query and nothing more."
    )