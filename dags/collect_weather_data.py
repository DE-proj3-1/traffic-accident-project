from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.providers.amazon.aws.hooks.s3 import S3Hook
from datetime import datetime, timedelta
import pandas as pd
import requests
import json
import io

def is_json(response_text):
    try:
        json_object = json.loads(response_text)
    except ValueError as e:
        return False
    return True

def collect_weather_data(service_key, nx_range, ny_range):
    weather_data = []
    for nx in nx_range:
        for ny in ny_range:
            now = datetime.now()
            base_date = now.strftime("%Y%m%d")
            base_time = (now - timedelta(hours=1)).strftime("%H%M")
            url = f"http://apis.data.go.kr/1360000/VilageFcstInfoService_2.0/getUltraSrtFcst?serviceKey={service_key}&numOfRows=60&pageNo=1&dataType=json&base_date={base_date}&base_time={base_time}&nx={nx}&ny={ny}"
            response = requests.get(url, verify=False)
            print(f"Status code: {response.status_code}")
            print(f"Response content: {response.text}")
            
            
            if is_json(response.text):
                res = json.loads(response.text)
                weather_data.append(res)
            else:
                print(f"Received non-JSON response: {response.text}")

    return weather_data

def transform_data(weather_data):
    transformed_data = []

    for data in weather_data:
        items = data['response']['body']['items']['item']
        df = pd.DataFrame(items)
        grouped = df.groupby(['baseDate', 'baseTime','nx','ny'])
        transformed_df = grouped.apply(lambda g: pd.Series({category: fcstValue for category, fcstValue in zip(g['category'], g['fcstValue'])}))
        transformed_data.append(transformed_df.reset_index())

    # 최종 데이터프레임을 문자열로 변환하여 반환합니다.
    csv_buffer = io.StringIO()
    final_df = pd.concat(transformed_data, ignore_index=True)
    final_df.to_csv(csv_buffer, index=False)
    return csv_buffer.getvalue()

def process_data(transformed_data, coord_df_key, s3_bucket):
    transformed_data = pd.read_csv(io.StringIO(transformed_data))

    hook = S3Hook(aws_conn_id='aws_s3_default')
    response = hook.get_key(coord_df_key, bucket_name=s3_bucket)
    
    response_object = response.get()
    response_body = response_object['Body']
    coord_df = pd.read_excel(io.BytesIO(response_body.read()))[['격자 X', '격자 Y', '1단계', '2단계', '3단계', '경도(초/100)', '위도(초/100)']]

    # coord_df = pd.read_excel(io.BytesIO(response.read()))[['격자 X', '격자 Y', '1단계', '2단계', '3단계', '경도(초/100)', '위도(초/100)']]
    # coord_df = pd.read_excel(coord_df_path)[['격자 X', '격자 Y', '1단계', '2단계', '3단계', '경도(초/100)', '위도(초/100)']]
    final_df = transformed_data.astype(str).merge(coord_df.astype(str), left_on=['nx', 'ny'], right_on=['격자 X', '격자 Y'])
    final_df.drop(['nx', 'ny','LGT','UUU','VVV'], axis=1, inplace=True)

    final_df.rename(columns={'baseDate':'curr_date', 'baseTime':'curr_time', 'PTY':'rain_form', 'RN1':'rain_per', 'SKY':'sky', 'REH':'humidity','T1H':'temp','VEC':'wind_direction', 'WSD':'wind_speed', '격자 X':'nx', '격자 Y':'ny', '1단계': 'si', '2단계': 'gu', '3단계': 'dong', '경도(초/100)': 'lon', '위도(초/100)': 'lat'}, inplace=True)
    final_df['curr_date'] = pd.to_datetime(final_df['curr_date'], format='%Y%m%d')
    final_df['curr_time'] = pd.to_datetime(final_df['curr_time'], format='%H%M').dt.time

    columns_to_convert = {'temp': float, 'humidity': int, 'wind_direction': int, 'wind_speed': int}
    final_df = final_df.astype(columns_to_convert)

    replace_values = {'0': '없음', '1': '비', '2': '비/눈', '3': '눈', '4': '소나기', '5': '빗방울', '6': '빗방울눈날림', '7': '눈날림'}
    final_df['rain_form'] = final_df['rain_form'].replace(replace_values)
    
    final_df['rain_per'] = final_df['rain_per'].str.replace('mm', '').replace('강수없음', '0').replace('1 미만', '0.5').astype(float)

    final_df['sky'] = final_df['sky'].replace({'1': '맑음', '3': '구름많음', '4': '흐림'})

    # 최종 데이터프레임을 문자열로 변환하여 반환합니다.
    csv_buffer = io.StringIO()
    final_df.to_csv(csv_buffer, index=False)
    return csv_buffer.getvalue()

def write_to_csv_and_upload_to_s3(final_df, s3_bucket, s3_key):
    hook = S3Hook(aws_conn_id='aws_s3_default')
    final_df = pd.read_csv(io.StringIO(final_df))

    if hook.check_for_key(s3_key, bucket_name=s3_bucket):
        # If file exists, download and convert to dataframe
        old_data_obj = hook.get_key(s3_key, bucket_name=s3_bucket)
        old_data = pd.read_csv(io.StringIO(old_data_obj.get()['Body'].read().decode('utf-8')))
        # Concat old and new data
        final_df = pd.concat([old_data, final_df], ignore_index=True)
        
    csv_buffer = io.StringIO()
    final_df.to_csv(csv_buffer, index=False)
    hook.load_string(
        string_data=csv_buffer.getvalue(),
        key=s3_key,
        bucket_name=s3_bucket,
        replace=True
    )

dag = DAG(
    'collect_and_process_data', 
    start_date=datetime(2024, 3, 6), 
    schedule_interval='*/30 * * * *'
    )

collect_weather_data_task = PythonOperator(
    task_id='collect_weather_data',
    python_callable=collect_weather_data,
    op_kwargs={
        'service_key': 'IFTPv5VE1vae2KeM4f%2B9ioopRF2QYG1RT5ddI8dcmacVYceg64F8zRlRJQXQha3BJkAwlSreLXh9%2FbwEdO%2FzmQ%3D%3D',
        'nx_range': range(57, 64),
        'ny_range': range(124, 130)
    },
    dag=dag
)

transform_data_task = PythonOperator(
    task_id='transform_data',
    python_callable=transform_data,
    op_kwargs={'weather_data': collect_weather_data_task.output},
    dag=dag
)

process_data_task = PythonOperator(
    task_id='process_data',
    python_callable=process_data,
    op_kwargs={
        'transformed_data': transform_data_task.output,
        's3_bucket': 'de-3-1-bucket',
        'coord_df_key': 'test/coordinate_file.xlsx'
    },
    dag=dag
)

write_to_csv_and_upload_to_s3_task = PythonOperator(
    task_id='write_to_csv_and_upload_to_s3',
    python_callable=write_to_csv_and_upload_to_s3,
    op_kwargs={
        'final_df': process_data_task.output,
        's3_bucket': 'de-3-1-bucket',
        's3_key': 'acc/weather_data.csv'
    },
    dag=dag
)

collect_weather_data_task >> transform_data_task >> process_data_task >> write_to_csv_and_upload_to_s3_task