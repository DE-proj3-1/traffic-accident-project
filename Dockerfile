# Airflow image
FROM apache/airflow:2.5.1

# User root to install airflow packages
USER root

# Install airflow packages
RUN pip install apache-airflow-providers-amazon

# Switch back to airflow
USER airflow

# Copy dags to the dags directory
COPY dags/ /opt/airflow/dags/

# The default command, start airflow webserver and scheduler
CMD ["airflow", "scheduler", "&", "airflow", "webserver"]
