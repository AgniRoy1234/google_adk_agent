from google.cloud import bigquery
from dotenv import load_dotenv
load_dotenv()

from .connections1 import connect_to_cloudsql_mysql, connect_to_bigquery

from sqlalchemy import text, create_engine


def execute_select_cloudsql(query: str, params: dict = None) -> list[dict]:
  """Executes a SELECT query on the Cloud SQL MySQL instance

  and returns the results as a list of dictionaries.
  """
  # Create a SQLAlchemy engine using the Cloud SQL connector creator
  engine = create_engine(
      "mysql+pymysql://", creator=connect_to_cloudsql_mysql
  )

  with engine.connect() as connection:
    # Execute query, optionally with parameters to prevent SQL injection
    result = connection.execute(text(query), params or {})
    # Fetch column names and map rows to dictionaries
    columns = result.keys()
    rows = result.fetchall()
    result_list = [dict(zip(columns, row)) for row in rows]

  return result_list


def execute_write_cloudsql(query: str, params: dict = None) -> int:
  """Executes an INSERT, UPDATE, or DELETE query on the Cloud SQL MySQL instance

  and returns the number of affected rows.
  """
  engine = create_engine(
      "mysql+pymysql://", creator=connect_to_cloudsql_mysql
  )

  with engine.connect() as connection:
    with connection.begin():  # Manages transaction commit/rollback
      result = connection.execute(text(query), params or {})
      affected_rows = result.rowcount
  return affected_rows


def execute_select_bigquery(query, params=None):
    """Executes a SELECT query on BigQuery and returns the results as a list of dictionaries."""
    try:
        client = connect_to_bigquery()
        
        # Configure query parameters if passed (BigQuery uses QueryJobConfig for params)
        job_config = None
        if params:
            job_config = bigquery.QueryJobConfig(query_parameters=params)
            
        query_job = client.query(query, job_config=job_config)
        results = query_job.result()  
        
        # BigQuery Row objects can be directly converted or mapped to dicts
        return [dict(row.items()) for row in results]
    except Exception as e:
        print(f"BigQuery select error: {e}")
        raise


def execute_write_bigquery(query, params=None):
    """Executes an INSERT, UPDATE, or DDL statement (Data Manipulation Language) in BigQuery."""
    try:
        client = connect_to_bigquery()
        
        job_config = None
        if params:
            job_config = bigquery.QueryJobConfig(query_parameters=params)
            
        query_job = client.query(query, job_config=job_config)
        query_job.result()  # Waits for the write/DML job to finish executing
    except Exception as e:
        print(f"BigQuery write error: {e}")
        raise