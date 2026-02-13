import pathlib

import psycopg2


DB_HOST = "airflow-postgres"
DB_PORT = 5432
DB_NAME = "airflow"
DB_USER = "airflow"
DB_PASSWORD = "airflow"


def main() -> None:
    schema_path = pathlib.Path("/opt/airflow/project/db/schema.sql")
    if not schema_path.exists():
        raise FileNotFoundError(f"schema.sql not found at {schema_path}")

    with psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
    ) as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT to_regclass('public.ingestion_state')")
            exists = cur.fetchone()[0]
            if exists:
                print("Schema already initialized; skipping.")
                return

            sql = schema_path.read_text()
            cur.execute(sql)
            print("Schema initialized successfully.")


if __name__ == "__main__":
    main()
