from datetime import datetime, timedelta
import json
from pathlib import Path

import psycopg2
from airflow import DAG
from airflow.exceptions import AirflowFailException
from airflow.operators.python import PythonOperator

DB = {
    "host": "airflow-postgres",
    "port": 5432,
    "dbname": "airflow",
    "user": "airflow",
    "password": "airflow",
}

OUT = Path("/opt/airflow/project/analytics/dashboards/data/overview.json")


def validate_analytics_data():
    with psycopg2.connect(**DB) as conn, conn.cursor() as cur:
        cur.execute("SELECT COUNT(*) FROM analytics.analytics_listening_events")
        cnt = cur.fetchone()[0]
        if cnt == 0:
            raise AirflowFailException("No analytics data available yet.")


def build_dashboard_snapshot():
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with psycopg2.connect(**DB) as conn, conn.cursor() as cur:
        cur.execute("""
            SELECT user_id, total_plays, unique_artists, unique_tracks
            FROM analytics.analytics_user_metrics
            ORDER BY total_plays DESC
            LIMIT 100
        """)
        rows = cur.fetchall()
    payload = [
        {
            "user_id": r[0],
            "total_plays": r[1],
            "unique_artists": r[2],
            "unique_tracks": r[3],
        }
        for r in rows
    ]
    OUT.write_text(json.dumps(payload, indent=2), encoding="utf-8")


with DAG(
    dag_id="marimo_dashboard_refresh",
    start_date=datetime(2026, 2, 9),
    schedule="5,35 * * * *",
    catchup=False,
    max_active_runs=1,
    default_args={"owner": "data-platform", "retries": 1, "retry_delay": timedelta(minutes=2)},
) as dag:
    t1 = PythonOperator(task_id="validate_analytics_data", python_callable=validate_analytics_data)
    t2 = PythonOperator(task_id="build_dashboard_snapshot", python_callable=build_dashboard_snapshot)
    t1 >> t2
