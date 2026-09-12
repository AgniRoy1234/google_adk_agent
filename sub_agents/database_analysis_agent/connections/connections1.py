import os 
from google.cloud import bigquery
from dotenv import load_dotenv
load_dotenv()

from google.cloud.sql.connector import Connector
import pandas as pd

CLOUDSQL_DB_USER = os.getenv("CLOUDSQL_DB_USER")
CLOUDSQL_DB_PASS = os.getenv("CLOUDSQL_DB_PASS")
CLOUDSQL_DB_NAME = os.getenv("CLOUDSQL_DB_NAME")
CLOUDSQL_INSTANCE_CONNECTION_NAME = (os.getenv(
    "CLOUDSQL_INSTANCE_CONNECTION_NAME"
))

def connect_to_cloudsql_mysql():
    """Establishes and returns a secure connection to the AWS RDS PostgreSQL database."""
    connector = Connector()
    conn = connector.connect(
          CLOUDSQL_INSTANCE_CONNECTION_NAME,
          "pymysql",
          user=CLOUDSQL_DB_USER,
          password=CLOUDSQL_DB_PASS,
          db=CLOUDSQL_DB_NAME)
    return conn

def connect_to_bigquery():
    """Establishes and returns a BigQuery client using project ID from environment variables."""
    project_id = os.getenv("GCP_PROJECT_ID")
    # BigQuery uses application default credentials (ADC). 
    # Ensure GOOGLE_APPLICATION_CREDENTIALS path environment variable is set if running locally.
    return bigquery.Client(project=project_id)