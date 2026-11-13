
import psycopg2
import pandas as pd

def get_connection():
    return psycopg2.connect(
        host="localhost",
        database="titanic_db",
        user="postgres",
        password="Password",
        port="5432",
        options="-c search_path=titanic_project,public"
    )


def run_query(query, params=None):
    conn = get_connection()

    try:
        with conn.cursor() as cur:
            cur.execute(query, params)

            if cur.description:
                rows = cur.fetchall()
                columns = [desc[0] for desc in cur.description]

                return pd.DataFrame(rows, columns=columns)

            return pd.DataFrame()

    finally:
        conn.close()


if __name__ == "__main__":
    result = run_query(
        "SELECT COUNT(*) AS total FROM passengers"
    )
    print(result)
