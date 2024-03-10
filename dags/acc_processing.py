from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.providers.amazon.aws.hooks.s3 import S3Hook
from airflow.exceptions import AirflowException
import pandas as pd
import numpy as np
from geopy.geocoders import Nominatim
import pyproj
import logging
from io import BytesIO, StringIO
from datetime import datetime, timedelta

def check_s3_connection(s3_bucket, s3_key):
    hook = S3Hook(aws_conn_id='aws_conn_id')
    response = hook.get_key(s3_key, bucket_name=s3_bucket)

    response_object = response.get()
    response_body = response_object['Body'].read()
    df_from_csv = pd.read_csv(BytesIO(response_body))
    
    if len(df_from_csv) > 0:
        logging.info(f"{len(df_from_csv)} : 파일 연결 성공")
        df_from_csv = df_from_csv.dropna()
        logging.info(f"{len(df_from_csv)} : 빈 행 처리")
    else:
        raise AirflowException("파일이 존재하지 않습니다.")

    return df_from_csv

def int_to_date(col):
    return pd.to_datetime(col.astype(str), format='%Y%m%d')

def clean_data(df):
    df_cleaned = df.dropna()
    columns_to_convert = ['occr_time', 'exp_clr_date', 'exp_clr_time', 'link_id', 'acc_road_code']
    df_cleaned[columns_to_convert] = df_cleaned[columns_to_convert].astype(int)

    date_columns = ['occr_date', 'exp_clr_date']
    df_cleaned[date_columns] = df_cleaned[date_columns].apply(int_to_date)

    return df_cleaned

def utm_to_latlng(row):
    p1_type = "epsg:2097"
    p2_type = "epsg:4326"
    p1 = pyproj.Proj(init=p1_type)
    p2 = pyproj.Proj(init=p2_type)
    fx, fy = pyproj.transform(p1, p2, row['grs80tm_x'], row['grs80tm_y'])
    return pd.Series({'longitude': fx, 'latitude': fy})

def update_lat_lng(df):
    df[['longitude', 'latitude']] = df.apply(utm_to_latlng, axis=1)
    return df

def geocoding_reverse(row):
    geolocoder = Nominatim(user_agent = 'South Korea', timeout=None)
    latitude = row['latitude']
    longitude = row['longitude']
    if pd.isnull(latitude) or pd.isnull(longitude):
      return pd.Series({'address': np.nan})

    address = geolocoder.reverse(f"{latitude}, {longitude}")
    addr_split = address[0].split(',')
    s = [addr.strip() for addr in addr_split]
    s.reverse()
    addr_str = ' '.join(s[2:])

    return pd.Series({'address' : addr_str})

def update_address(df):
    df[['address']] = df.apply(geocoding_reverse, axis=1)
    return df

def save_as_csv_to_s3(df, s3_bucket, s3_key):
    hook = S3Hook(aws_conn_id='aws_conn_id')
    csv_buffer = StringIO()
    df.to_csv(csv_buffer, index=False, encoding='utf-8')
    hook.load_string(
        string_data=csv_buffer.getvalue(),
        key=s3_key,
        bucket_name=s3_bucket,
        replace=True
    )
    logging.info("s3 업로드")

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime.now() - timedelta(hours=1),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'catchup' : False
}

with DAG('location_update_dag',
         default_args=default_args,
         description='Add latitude, longitude, address columns to Seoul Live Accident CSV',
         schedule_interval='0 * * * *') as dag:
    
    check_s3_connection_task = PythonOperator(
        task_id='check_s3_connection_task',
        python_callable=check_s3_connection,
        op_kwargs={
        's3_bucket': 'de-3-1-bucket',
        's3_key': 'acc/seoul_live_acc.csv'
        }
    )

    clean_data_task = PythonOperator(
        task_id='clean_data_task',
        python_callable=clean_data,
        op_args=[check_s3_connection_task.output],
    )

    update_lat_lng_task = PythonOperator(
        task_id='update_lat_lng',
        python_callable=update_lat_lng,
        op_args=[clean_data_task.output],
    )

    update_address_task = PythonOperator(
        task_id='update_address_task',
        python_callable=update_address,
        op_args=[update_lat_lng_task.output],
    )

    save_as_csv_to_s3_task = PythonOperator(
        task_id='save_csv_task',
        python_callable=save_as_csv_to_s3,
        op_kwargs={
        'df': update_address_task.output,
        's3_bucket': 'de-3-1-bucket',
        's3_key': 'acc/seoul_live_acc_with_location.csv'
        },
    )    

check_s3_connection_task >> clean_data_task >> update_lat_lng_task >> update_address_task >> save_as_csv_to_s3_task
