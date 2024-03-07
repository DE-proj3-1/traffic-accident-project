from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.hooks.S3_hook import S3Hook
from airflow.hooks.mysql_hook import MySqlHook
from sqlalchemy import create_engine
import pandas as pd
from io import StringIO

def transfer_s3_to_rds(*args, **kwargs):
    s3 = S3Hook(aws_conn_id='aws_s3_default')
    rds = MySqlHook(mysql_conn_id='aws_rds_default')

    bucket_name = 'de-3-1-bucket'
    key = 'acc/weather_data.csv'
    s3_file_obj = s3.get_key(bucket_name=bucket_name, key=key)
    s3_file = s3_file_obj.get()['Body'].read().decode('utf-8')

    data = pd.read_csv(StringIO(s3_file))

    conn = rds.get_connection(rds.mysql_conn_id)
    engine = create_engine(f"mysql+pymysql://{conn.login}:{conn.password}@{conn.host}/{conn.schema}")

    data.to_sql('live_weather', engine, if_exists='replace', index=False)

default_args = {
    'owner': 'airflow',
    'start_date': datetime(2024, 3, 7),
    'retries': 1,
    'retry_delay': timedelta(minutes=5)
}

dag = DAG(
    's3_to_rds_dag',
    default_args=default_args,
    description='A simple tutorial DAG',
    schedule_interval=timedelta(days=1),
    catchup=False
)

transfer_s3_to_rds = PythonOperator(
    task_id='s3_to_rds',
    python_callable=transfer_s3_to_rds,
    provide_context=True,
    dag=dag,
)
