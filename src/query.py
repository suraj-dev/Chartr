from dotenv import load_dotenv
load_dotenv()
import openai
import os
from src.db import get_connection
from langchain.tools import tool

openai_api_key = os.getenv("OPENAI_KEY")
openai_api_base = os.getenv("LLM_HOST")
client = None
schema_str = None
def get_openai_client() -> openai.OpenAI:
    global client
    if client is None:
        client = openai.OpenAI(api_key=openai_api_key, base_url=openai_api_base)
    return client

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

@tool
def verify_sql_query(sql_query: str) -> str:
    """Run the provided SQL query and return the result status."""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(sql_query)
        result = cursor.fetchone()
        if result is not None and len(result) > 0:
            return "success"
        else:
            return "no_results"
    except Exception as e:
        return f"error: {e}"
def run_nl_to_sql_with_verification(nl_query):
    schema_description = extract_db_schema()
    # Build the prompt string
    prompt_str = (
        f"You are an SQL expert. Given the database schema:\n"
        f"{schema_description}\n\n"
        f"Convert the user request into a SQL query.\n"
        f"Return only the SQL, no explanation.\n\n"
        f"User request: '{nl_query}'\n"
    )
    # Call the local LMStudio endpoint via OpenAI client
    client = get_openai_client()
    response = client.chat.completions.create(
        model="sqlcoder-7b-2",
        messages=[{"role": "user", "content": prompt_str}],
        temperature=0.0
    )
    # Extract and return the SQL text
    query = response.choices[0].message.content.strip()
    max_retries = 3
    for i in range(max_retries):
        result = verify_sql_query(query)
        if result == "success":
            return query
        elif result == "no_results":
            retry_prompt_str = (
                f"The SQL query below returned no results. Please try again.\n\n"
                f"SQL query: '{query}'\n"
                f"Given the database schema:\n"
                f"{schema_description}\n\n"
                f"Convert the user request into a SQL query.\n"
                f"Return only the SQL, no explanation.\n\n"
                f"User request: '{nl_query}'\n"
            )
            response = client.chat.completions.create(
                model="sqlcoder-7b-2",
                messages=[{"role": "user", "content": retry_prompt_str}],
                temperature=0.0
            )
            query = response.choices[0].message.content.strip()
        else:
            return f"Error executing query: {query}"