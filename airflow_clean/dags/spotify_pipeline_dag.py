from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.bash import BashOperator


default_args = {
    "owner": "data-platform",
    "retries": 2,
    "retry_delay": timedelta(minutes=5),
}

with DAG(
    dag_id="spotify_data_pipeline",
    description="Spotify ingestion, QA, and analytics pipeline",
    start_date=datetime(2026, 2, 9),
    schedule="*/30 * * * *",
    catchup=False,
    default_args=default_args,
    max_active_runs=5,
    tags=["spotify", "pipeline"],
) as dag:
    ingest = BashOperator(
        task_id="ingest_listening",
        bash_command="cd /opt/airflow/project && python ingestion/ingestion_listening.py",
    )

    qa = BashOperator(
        task_id="qa_checks",
        bash_command="cd /opt/airflow/project && python qa/run_qa.py",
    )

    analytics = BashOperator(
        task_id="build_analytics",
        bash_command="cd /opt/airflow/project && python analytics/pipelines/build_analytics_tables.py",
    )

    ingest >> qa >> analytics
