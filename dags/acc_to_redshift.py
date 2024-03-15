from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.hooks.S3_hook import S3Hook
from airflow.hooks.postgres_hook import PostgresHook

def transfer_s3_to_redshift(*args, **kwargs):
    s3 = S3Hook(aws_conn_id='aws_conn_id')
    redshift = PostgresHook(postgres_conn_id='aws_redshift_default')
    bucket_name = 'de-3-1-bucket'
    key = 'acc/seoul_live_acc_with_location.csv'
    s3_file_path = f"s3://{bucket_name}/{key}"
    credentials = s3.get_credentials()
    access_key = credentials.access_key
    secret_key = credentials.secret_key
    drop_table_query = """
    DROP TABLE IF EXISTS raw_data.accident;
    """
    redshift.run(drop_table_query)
    create_table_query = """

    CREATE TABLE IF NOT EXISTS raw_data.accident (
        acc_id INTEGER NOT NULL,
        occr_date DATE,
        occr_time VARCHAR(65535),
        exp_clr_date DATE,
        exp_clr_time INTEGER ,
        acc_type VARCHAR(65535),
        acc_dtype VARCHAR(65535),
        link_id VARCHAR(65535),
        grs80tm_x FLOAT,
        grs80tm_y FLOAT,
        acc_info VARCHAR(65535),
        acc_road_code INTEGER,
        longitude FLOAT,
        latitude FLOAT,
        address VARCHAR(65535)
    );
    """
    redshift.run(create_table_query)
    copy_query = f"""
    COPY raw_data.accident
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
    'accident_s3_to_redshift_dag',
    default_args=default_args,
    description='Add seoul live accident data to redshift',
    schedule_interval=timedelta(minutes=10),
    catchup=False
)
transfer_s3_to_redshift = PythonOperator(
    task_id='s3_to_redshift',
    python_callable=transfer_s3_to_redshift,
    provide_context=True,
    dag=dag,
)