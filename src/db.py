from dotenv import load_dotenv
import psycopg2
import os
import atexit

load_dotenv()

_connection = None


def get_connection():
    global _connection
    if _connection is None:
        try:
            _connection = psycopg2.connect(
                database=os.getenv("POSTGRES_DB"),
                user=os.getenv("POSTGRES_USER"),
                password=os.getenv("POSTGRES_PASSWORD"),
                host=os.getenv("POSTGRES_HOST"),
                port=os.getenv("POSTGRES_PORT"),
            )
            print("Successfully connected to PostgreSQL")
        except psycopg2.Error as e:
            print(f"Error connecting to PostgreSQL: {e}")
            close_connection()
    return _connection


def close_connection():
    global _connection
    if _connection:
        _connection.close()
        _connection = None
        print("PostgreSQL connection closed")


atexit.register(close_connection)

if __name__ == "__main__":
    conn = get_connection()
    print("Database setup complete!")
