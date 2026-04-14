FROM quay.io/astronomer/astro-runtime:12.4.0

USER root
RUN apt-get update && apt-get install -y gcc python3-dev && apt-get clean

USER 50000

WORKDIR "/usr/local/airflow"
COPY dbt-requirements.txt ./
RUN python -m venv dbt_venv && \
    ./dbt_venv/bin/pip install --no-cache-dir -r dbt-requirements.txt