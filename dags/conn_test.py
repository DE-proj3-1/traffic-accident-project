from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.providers.amazon.aws.hooks.s3 import S3Hook
from datetime import datetime

def collect_and_store_data(**kwargs):
    hook = S3Hook(aws_conn_id='aws_s3_default')
    data = 'Hello, World!'
    # 수집한 데이터를 S3에 업로드합니다.
    hook.load_string(
        string_data=data,
        key='test/hello.txt',
        bucket_name='de-3-1-bucket',
        replace=True
    )

dag = DAG('collect_and_store_data', start_date=datetime(2022, 1, 1))

collect_and_store_data_task = PythonOperator(
    task_id='collect_and_store_data',
    python_callable=collect_and_store_data,
    dag=dag
)
