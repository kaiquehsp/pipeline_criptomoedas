import os
from datetime import datetime
from pathlib import Path
from airflow.decorators import dag, task
from cosmos import DbtTaskGroup, ProjectConfig, ProfileConfig, ExecutionConfig
from include.ingest import extract_and_save 

BASE_PATH = Path("/usr/local/airflow")

DBT_PROJECT_PATH = BASE_PATH / "dbt" / "projeto_engenharia" / "dbt_code"

DBT_EXECUTABLE_PATH = BASE_PATH / "dbt_venv" / "bin" / "dbt"

profile_config = ProfileConfig(
    profile_name="dbt_code",  
    target_name="dev",
    profiles_yml_filepath=DBT_PROJECT_PATH / "profiles.yml",
)

@dag(
    dag_id="crypto_medallion_pipeline",
    start_date=datetime(2026, 4, 8),
    schedule="@daily",
    catchup=False,
    max_active_tasks=1,  
    max_active_runs=1,
)
def crypto_dag():

    @task(task_id="ingestion_layer_bronze")
    def ingestion_layer():
        extract_and_save()

    transform_layer = DbtTaskGroup(
        group_id="dbt_transformations",
        project_config=ProjectConfig(str(DBT_PROJECT_PATH)),
        profile_config=profile_config,
        execution_config=ExecutionConfig(dbt_executable_path=str(DBT_EXECUTABLE_PATH)),
    )

    ingestion_layer() >> transform_layer

crypto_dag()