import psycopg2
import psycopg2.extras
from psycopg2.extras import DictCursor
from psycopg2 import sql
from config import DB_NAME, USER, PASSWORD, HOST, PORT, CHUNK_SIZE
import pandas as pd


def init_connection(dbname=DB_NAME, user=USER, password=PASSWORD, host=HOST, port=PORT, load=True):
    """Establishes connection to Postgres database.

    Args:
        dbname (str, optional): database name. Defaults to DB_NAME.
        user (str, optional): user name. Defaults to USER.
        password (str, optional): password. Defaults to PASSWORD.
        host (str, optional): host. Defaults to HOST.
        port (str, optional): port. Defaults to PORT.
        load (bool, optional): True if loading into db. False if fetching from db. Defaults to True.

    Returns:
        tuple[obj,obj]: connection (conn), cursor (cur) 
    """
    conn = psycopg2.connect(dbname=dbname, user=user, password=password, host=host, port=port)
    if load:
        cur = conn.cursor()
    else:
        cur = conn.cursor(cursor_factory=DictCursor)
    return conn, cur

def create_db():
    try:
        # Connect to PostgreSQL default database
        conn, cur = init_connection(dbname="postgres")
        conn.autocommit = True  # Enable autocommit for creating a database
        

        # Create database
        cur.execute(sql.SQL("CREATE DATABASE {}").format(sql.Identifier(DB_NAME)))
        print(f"Database {DB_NAME} created successfully.")
        
    except Exception as e:
        print(f'Error creating database: {e}')
        
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()
        
        
def create_table():
    try:
        conn, cur = init_connection()

        # Create table without embeddings
        cur.execute("""
            CREATE TABLE IF NOT EXISTS listings (
                listing_id TEXT PRIMARY KEY,
                title TEXT,
                description TEXT,
                price NUMERIC,
                city TEXT,
                state TEXT,
                year INT,
                make TEXT,
                model TEXT,
                transmission TEXT,
                exterior_color TEXT,
                interior_color TEXT,
                category TEXT
            )
        """)
        conn.commit()
        
    except Exception as e:
        print(f'Error creating table: {e}')
        
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()
        

def insert_data(df: pd.DataFrame, chunk_size: int=CHUNK_SIZE) -> None:
    try:
        conn, cur = init_connection()
        cols = ",".join(df.columns)
        values_template = ",".join(["%s"] * len(df.columns))
        insert_query = f"""INSERT INTO listings ({cols}) 
                           VALUES ({values_template}) 
                           ON CONFLICT (listing_id) DO NOTHING"""
        
        for i in range(0, len(df), chunk_size):
            try:
                chunk = df.iloc[i:i + chunk_size].values.tolist()
                psycopg2.extras.execute_batch(cur, insert_query, chunk)
            except Exception as e:
                print(f'Failed to insert rows{i}-{i+chunk_size}: {e}')
        
        conn.commit()
        
    except Exception as e:
        print(f'Error: {e}')
        
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()
            


if __name__=='__main__':
    # create_db()
    create_table()