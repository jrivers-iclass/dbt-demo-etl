`docker compose up -d`

We use Airflow to schedule the DAG to run hourly.
Airflow is running on port 8080.
Default username and password is `admin`.

Activate the `mysql_to_postgres_dag` in the Airflow UI to run the DAG.

Postgres database is running on port 5432.
The database name is `analytics`.
The `public` schema is used for the demo project.
To login to the Postgres database, use the following command:
`psql -h localhost -U dbtuser -d analytics`


DBT models are in the `demo_project` directory under the `models` folder. 
