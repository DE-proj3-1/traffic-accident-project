from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.hooks.S3_hook import S3Hook
from airflow.hooks.postgres_hook import PostgresHook

def transfer_s3_to_redshift(*args, **kwargs):
    s3 = S3Hook(aws_conn_id='aws_s3_default')
    redshift = PostgresHook(postgres_conn_id='aws_redshift_default')

    bucket_name = 'de-3-1-bucket'
    key = 'acc/death_acc_data.csv'
    s3_file_path = f"s3://{bucket_name}/{key}"

    credentials = s3.get_credentials()
    access_key = credentials.access_key
    secret_key = credentials.secret_key
    
    
    create_table_query = """
    CREATE TABLE IF NOT EXISTS raw_data.death_acc_info (
        death_id INTEGER,
        occ_date TIMESTAMP,
        day_night VARCHAR(256),
        day_week VARCHAR(256),
        num_dea INTEGER,
        num_cas INTEGER,
        num_seri INTEGER,
        num_min INTEGER,
        num_report INTEGER,
        si VARCHAR(256),
        gu VARCHAR(256),
        acc_type1 VARCHAR(256),
        acc_type2 VARCHAR(256),
        acc_type VARCHAR(256),
        law VARCHAR(256),
        load_type1 VARCHAR(256),
        load_type VARCHAR(256),
        acc_party1 VARCHAR(256),
        acc_party2 VARCHAR(256),
        lon DOUBLE PRECISION,
        lat DOUBLE PRECISION
    );
    """
    redshift.run(create_table_query)

    copy_query = f"""
    COPY raw_data.death_acc_info
    FROM '{s3_file_path}'
    ACCESS_KEY_ID '{access_key}'
    SECRET_ACCESS_KEY '{secret_key}'
    FORMAT AS CSV DELIMITER ',' QUOTE '"' IGNOREHEADER 1 REGION AS 'ap-northeast-2'
    """
    redshift.run(copy_query)

default_args = {
    'owner': 'airflow',
    'start_date': datetime(2024, 3, 7),
    'retries': 1,
    'retry_delay': timedelta(minutes=5)
}

dag = DAG(
    'death_acc_s3_to_redshift_dag',
    default_args=default_args,
    description='A simple tutorial DAG',
    schedule_interval=timedelta(days=1),
    catchup=False
)

transfer_s3_to_redshift = PythonOperator(
    task_id='s3_to_redshift',
    python_callable=transfer_s3_to_redshift,
    provide_context=True,
    dag=dag,
)
