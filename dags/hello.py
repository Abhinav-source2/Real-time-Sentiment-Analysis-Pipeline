from datetime import datetime
from airflow import DAG
from airflow.operators.python import PythonOperator

def say_hello():
    print("Hello, World from Airflow!")

with DAG(
    dag_id="hello_world_dag",
    start_date=datetime(2023, 1, 1),
    schedule="@daily",    # Use `schedule` instead of `schedule_interval`
    catchup=False,
    tags=["example"]
) as dag:

    hello_task = PythonOperator(
        task_id="say_hello_task",
        python_callable=say_hello
    )

    hello_task
