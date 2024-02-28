# Airflow image
FROM apache/airflow:2.5.1


USER airflow

# Install airflow packages
RUN pip install apache-airflow-providers-amazon

USER root

# Copy dags to the dags directory
COPY dags/ /opt/airflow/dags/

# The default command, start airflow webserver and scheduler
CMD ["airflow", "scheduler", "&", "airflow", "webserver"]
