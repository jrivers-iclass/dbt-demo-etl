from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.mysql.hooks.mysql import MySqlHook
from airflow.operators.bash import BashOperator
from airflow.decorators import task
from datetime import datetime, timedelta
import logging
import os
import yaml
import pandas as pd

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
    'start_date': datetime(2024, 1, 1),
}

def get_mysql_tables(**context):
    logger = logging.getLogger(__name__)
    mysql_hook = MySqlHook(mysql_conn_id='mysql_source')
    
    try:
        logger.info("Executing SHOW TABLES query...")
        tables_query = "SHOW TABLES"
        tables = mysql_hook.get_records(tables_query)
        table_list = [table[0] for table in tables]
        logger.info(f"Found tables: {table_list}")
        
        # Push the table list to XCom
        context['task_instance'].xcom_push(key='mysql_tables', value=table_list)
        return table_list
    except Exception as e:
        logger.error(f"Error getting MySQL tables: {str(e)}", exc_info=True)
        raise

def update_sources_yml(**context):
    logger = logging.getLogger(__name__)
    sources_file = '/opt/airflow/dbt/demo_project/models/example/sources.yml'
    
    # Get tables from XCom
    tables = context['task_instance'].xcom_pull(task_ids='get_tables', key='mysql_tables')
    
    sources_config = {
        'version': 2,
        'sources': [{
            'name': 'raw_data',
            'database': 'analytics',
            'schema': 'public_raw_data',
            'tables': [{'name': f'mysql_{table.lower()}'} for table in tables]
        }]
    }
    
    os.makedirs(os.path.dirname(sources_file), exist_ok=True)
    
    try:
        with open(sources_file, 'w') as f:
            yaml.dump(sources_config, f, sort_keys=False)
        logger.info(f"Updated sources.yml with {len(tables)} tables")
    except Exception as e:
        logger.error(f"Error updating sources.yml: {str(e)}", exc_info=True)
        raise

def extract_mysql_data(table_name, **context):
    logger = logging.getLogger(__name__)
    
    try:
        logger.info(f"Starting extraction for table: {table_name}")
        
        seeds_dir = '/opt/airflow/dbt/demo_project/seeds'
        os.makedirs(seeds_dir, exist_ok=True)
        
        mysql_hook = MySqlHook(mysql_conn_id='mysql_source')
        
        logger.info("Executing MySQL query...")
        query = f"SELECT * FROM {table_name}"
        logger.info(f"Query: {query}")
        df = mysql_hook.get_pandas_df(query)
        logger.info(f"Retrieved {len(df)} rows from {table_name}")
        
        output_path = f'{seeds_dir}/mysql_{table_name.lower()}.csv'
        logger.info(f"Saving data to: {output_path}")
        df.to_csv(output_path, index=False)
        
        logger.info(f"Successfully saved {table_name} data to CSV")
        return output_path
    except Exception as e:
        logger.error(f"Error extracting data from {table_name}: {str(e)}", exc_info=True)
        raise

with DAG(
    'mysql_to_postgres_etl',
    default_args=default_args,
    description='ETL from MySQL to Postgres using DBT',
    schedule_interval='0 * * * *',
    catchup=False
) as dag:

    get_tables = PythonOperator(
        task_id='get_tables',
        python_callable=get_mysql_tables,
    )

    update_sources = PythonOperator(
        task_id='update_sources',
        python_callable=update_sources_yml,
    )

    # Define a static list of tables we know exist
    static_tables = ['OrderDetails', 'Users', 'WeirdTable']
    extract_tasks = []
    
    for table in static_tables:
        task = PythonOperator(
            task_id=f'extract_{table}',
            python_callable=extract_mysql_data,
            op_kwargs={'table_name': table},
        )
        extract_tasks.append(task)

    dbt_seed = BashOperator(
        task_id='dbt_seed',
        bash_command='cd /opt/airflow/dbt/demo_project && dbt seed',
    )

    dbt_run = BashOperator(
        task_id='dbt_run',
        bash_command='cd /opt/airflow/dbt/demo_project && dbt run',
    )

    # Set up dependencies
    get_tables >> update_sources
    for task in extract_tasks:
        update_sources >> task >> dbt_seed
    dbt_seed >> dbt_run
