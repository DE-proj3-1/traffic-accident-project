from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.hooks.postgres_hook import PostgresHook

def test_redshift_connection(*args, **kwargs):
    redshift = PostgresHook(postgres_conn_id='aws_redshift_default')

    test_query = "SELECT 1"
    redshift.get_records(test_query)

default_args = {
    'owner': 'airflow',
    'start_date': datetime(2024, 3, 7),
    'retries': 1,
    'retry_delay': timedelta(minutes=5)
}

dag = DAG(
    'redshift_conn_test_dag',
    default_args=default_args,
    description='A simple Redshift connection test DAG',
    schedule_interval="@once",
    catchup=False
)

test_redshift_conn = PythonOperator(
    task_id='test_redshift_conn',
    python_callable=test_redshift_connection,
    provide_context=True,
    dag=dag,
)
