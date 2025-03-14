from airflow.utils.dates import days_ago
from airflow.sensors.external_task_sensor import ExternalTaskSensor
from datetime import datetime
from datetime import timedelta
from airflow import DAG
from airflow.providers.airbyte.operators.airbyte import AirbyteTriggerSyncOperator
from airflow.providers.airbyte.sensors.airbyte import AirbyteJobSensor
from airflow_dbt.operators.dbt_operator import DbtRunOperator
from airflow.operators.bash import BashOperator

default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "retries": 1,
    "dir": "/opt/airflow/dbt/test_project",
    "retry_delay": timedelta(minutes=1),
    "start_date": days_ago(1),
    "schedule_interval": "*/5 * * * *",
}

with DAG(
    dag_id="cartelis-test",
    default_args=default_args,
) as dag:

    sync_sale_data = AirbyteTriggerSyncOperator(
        task_id="sale_data-sync",
        airbyte_conn_id='airflow-airbyte-connection',
        connection_id="be033336-db0a-4027-a7b1-0fa0abb8dbb7",
    )

    sync_person_data = AirbyteTriggerSyncOperator(
        task_id="person_data-sync",
        airbyte_conn_id='airflow-airbyte-connection',
        connection_id="b8f24a42-5ef8-4a99-9a1b-fcaec8fbf07e",
    )
    
    dbt_run = BashOperator(
        task_id="dbt_run",
        bash_command="cd /opt/airflow/dbt/AdventureWorks/AdventureWorks/ && dbt run",
        dag=dag
    )
    [sync_person_data, sync_sale_data] >> dbt_run
