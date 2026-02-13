# Clean Airflow Runtime (spotify_data_pipeline)

This folder provides a clean Airflow setup to run `spotify_data_pipeline` with task logs visible in the Airflow UI.

## What this setup fixes
- Uses `LocalExecutor` to avoid Celery worker log routing issues.
- Mounts a shared logs folder (`./logs`) so the UI can display task logs directly.
- Forces project DB connection to `airflow-postgres` with `airflow/airflow` credentials.
- Runs one-time DB bootstrap (`schema.sql`) via `airflow-init`.

## Files
- `docker-compose.yml`: Airflow + Postgres stack
- `Dockerfile`: Airflow image with project Python deps
- `dags/spotify_pipeline_dag.py`: DAG definition
- `scripts/init_project_schema.py`: one-time schema bootstrap
- `logs/`: host-mounted Airflow logs for UI visibility

## Run
From this directory:

```bash
cd /Users/athishsn/Desktop/leetcode/dsa/spotify_airflow/airflow_clean
```

1) Build image:
```bash
docker compose build
```

2) Initialize Airflow DB, admin user, and project schema:
```bash
docker compose up airflow-init
```

3) Start scheduler + webserver:
```bash
docker compose up -d airflow-webserver airflow-scheduler
```

4) Open UI:
- http://localhost:8080
- username: `admin`
- password: `admin`

5) Trigger DAG:
```bash
docker compose exec airflow-webserver airflow dags unpause spotify_data_pipeline
docker compose exec airflow-webserver airflow dags trigger spotify_data_pipeline
```

## Verify logs in UI
- Open DAG run -> task -> Logs.
- Logs are also on host at:
`/Users/athishsn/Desktop/leetcode/dsa/spotify_airflow/airflow_clean/logs`

## Troubleshooting
1. Webserver not up:
```bash
docker compose logs --tail=200 airflow-webserver
```

2. Scheduler heartbeat issue:
```bash
docker compose logs --tail=200 airflow-scheduler
```

3. Reinitialize from scratch (removes Airflow metadata DB volume):
```bash
docker compose down -v
docker compose up airflow-init
docker compose up -d airflow-webserver airflow-scheduler
```
