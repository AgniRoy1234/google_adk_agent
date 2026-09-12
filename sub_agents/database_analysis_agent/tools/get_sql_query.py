import os
from pathlib import Path
from dotenv import load_dotenv
from ..llm.llm_provider import client, model_name
from ..prompts.prompts import cloudsql_prompt, bigquery_prompt

load_dotenv()

BIGQUERY_DATABASE = os.getenv("BIGQUERY_DATABASE")
CLOUDSQL_DB_NAME = os.getenv("CLOUDSQL_DB_NAME")

def get_big_query_sql(user_query: str):
  prompt = f"""You are a BigQuery SQL generator. Your task is to output ONLY a valid BigQuery SQL query that answers the user query based on the provided schema.

RULES:
1. Output ONLY the raw SQL code.
2. Do NOT wrap the SQL in markdown code blocks (e.g., do not use ```sql ... ```).
3. Do NOT include any explanations, greetings, or extra text.
4. The query must be directly executable in BigQuery.

BigQuery Database: {BIGQUERY_DATABASE}
Column Descriptions: {bigquery_prompt}
User Query: {user_query}

SQL Query:"""

  response = client.models.generate_content(model=model_name, contents=prompt)

  sql_query = response.text.strip()
  return sql_query


def get_cloudsql_sql(user_query: str) -> str:
  prompt = f"""You are an expert Cloud SQL MySQL database administrator and SQL generator. Your task is to output ONLY a valid MySQL SQL query that answers the user query based on the provided schema.

RULES:
1. Output ONLY the raw SQL code.
2. Do NOT wrap the SQL in markdown code blocks (e.g., do not use ```sql ... ```).
3. Do NOT include any explanations, greetings, or extra text.
4. Use standard MySQL syntax that is directly executable.

CLOUDSQL DATABASE: {CLOUDSQL_DB_NAME}
Column Descriptions: {cloudsql_prompt}
User Query: {user_query}

SQL Query:"""

  response = client.models.generate_content(model=model_name, contents=prompt)

  # Clean up output just in case stray markdown or whitespace is returned
  sql_query = (
      response.text.strip().removeprefix("```sql").removesuffix("```").strip()
  )
  return sql_query