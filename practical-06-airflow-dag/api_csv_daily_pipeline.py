# Name: Ayushman Rajeev Verma
# File: ~/airflow/dags/api_csv_daily_pipeline.py
import os
from datetime import datetime, timedelta
from airflow import DAG

try:                                            # Airflow 3.x import paths
    from airflow.providers.standard.operators.bash import BashOperator
    from airflow.providers.standard.operators.empty import EmptyOperator
    from airflow.providers.standard.operators.python import PythonOperator
except ImportError:                             # Airflow 2.x import paths
    from airflow.operators.bash import BashOperator
    from airflow.operators.empty import EmptyOperator
    from airflow.operators.python import PythonOperator

SCRIPT_DIR = os.path.expanduser("~/airflow/scripts")

def quality_check():
    """Fail the task when the report is missing or has too few rows."""
    import csv
    with open(os.path.join(SCRIPT_DIR, "todo_report.csv")) as f:
        rows = list(csv.DictReader(f))
    if len(rows) < 10:
        raise ValueError(f"Only {len(rows)} rows found - expected at least 10")
    print(f"Quality check passed: {len(rows)} rows in todo_report.csv")

with DAG(
    dag_id="api_csv_daily_pipeline",
    description="Daily API + CSV extraction followed by a quality check",
    start_date=datetime(2026, 1, 1),
    schedule="0 6 * * *",                       # every day at 06:00
    catchup=False,
    tags=["practical6", "etl"],
    default_args={"owner": "ayushman", "retries": 2, "retry_delay": timedelta(minutes=2)},
) as dag:

    begin = EmptyOperator(task_id="begin")

    fetch_and_clean = BashOperator(              # runs the program from Practical 5
        task_id="fetch_and_clean",
        bash_command=f"cd {SCRIPT_DIR} && python3 extract_pipeline.py",
    )

    check_quality = PythonOperator(task_id="check_quality", python_callable=quality_check)

    notify = BashOperator(
        task_id="notify_success",
        bash_command='echo "Pipeline finished OK on $(date +%F)"',
    )

    end = EmptyOperator(task_id="end")

    begin >> fetch_and_clean >> check_quality >> notify >> end
