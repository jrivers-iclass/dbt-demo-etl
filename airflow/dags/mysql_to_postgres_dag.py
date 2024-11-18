from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
from airflow.providers.mysql.hooks.mysql import MySqlHook
from airflow.providers.postgres.hooks.postgres import PostgresHook
from datetime import datetime, timedelta
import pandas as pd
from airflow.utils.log.logging_mixin import LoggingMixin
import logging
import os

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2024, 1, 1),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

def extract_mysql_data(table_name, **context):
    logger = logging.getLogger(__name__)
    
    try:
        logger.info(f"Starting extraction for table: {table_name}")
        
        # Create seeds directory if it doesn't exist
        seeds_dir = '/opt/airflow/dbt/demo_project/seeds'
        os.makedirs(seeds_dir, exist_ok=True)
        logger.info(f"Ensured seeds directory exists at: {seeds_dir}")
        
        mysql_hook = MySqlHook(mysql_conn_id='mysql_source')
        
        logger.info("Executing MySQL query...")
        df = mysql_hook.get_pandas_df(f"SELECT * FROM {table_name}")
        logger.info(f"Retrieved {len(df)} rows from {table_name}")
        
        # Save to CSV in the DBT seeds directory
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
    schedule_interval='0 * * * *',  # Run hourly
    catchup=False
) as dag:

    # Extract tasks
    extract_users = PythonOperator(
        task_id='extract_users',
        python_callable=extract_mysql_data,
        op_kwargs={'table_name': 'Users'},
        retries=3,
        retry_delay=timedelta(minutes=1),
        provide_context=True,
    )

    extract_orders = PythonOperator(
        task_id='extract_orders',
        python_callable=extract_mysql_data,
        op_kwargs={'table_name': 'OrderDetails'},
        retries=3,
        retry_delay=timedelta(minutes=1),
        provide_context=True,
    )

    # DBT tasks using BashOperator
    dbt_seed = BashOperator(
        task_id='dbt_seed',
        bash_command='''
            set -e
            cd /opt/airflow/dbt/demo_project && \
            DBT_PROFILES_DIR=/opt/airflow/dbt/demo_project \
            dbt seed --full-refresh
        ''',
        retries=3,
        retry_delay=timedelta(minutes=1),
    )

    dbt_run = BashOperator(
        task_id='dbt_run',
        bash_command='''
            set -e
            
            # Create writable logs directory in /tmp
            mkdir -p /tmp/dbt/logs
            
            # Run DBT with environment variables
            cd /opt/airflow/dbt/demo_project && \
            DBT_PROFILES_DIR=/opt/airflow/dbt/demo_project \
            DBT_LOG_PATH=/tmp/dbt/logs \
            dbt run --full-refresh
        ''',
        retries=3,
        retry_delay=timedelta(minutes=1),
    )

    # Dependencies
    [extract_users, extract_orders] >> dbt_seed >> dbt_run
