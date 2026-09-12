from ..tools.get_sql_query import get_big_query_sql, get_cloudsql_sql
from ..connections.query_select_and_execute import (
    execute_select_bigquery,
    execute_select_cloudsql,
)
from ..tools.save_artefacts import save_content_as_artifact

from google.adk.tools.tool_context import ToolContext
from google.genai import types

import logging
import json

import uuid

MAX_TOOL_CALLS = 3

import csv
import io
import pandas as pd


def convert_to_csv_bytes(data_list: list[dict]) -> bytes:
  """Convert a list of dictionaries into valid CSV bytes safely."""
  if not data_list:
    return b""

  # Use StringIO to hold the text-based CSV data in memory
  output = io.StringIO()

  # Extract fieldnames from the first dictionary
  fieldnames = list(data_list[0].keys())

  writer = csv.DictWriter(
      output,
      fieldnames=fieldnames,
      extrasaction="ignore",
      lineterminator="\n",  # Ensures consistent line endings across operating systems
  )

  writer.writeheader()
  writer.writerows(data_list)

  # Retrieve the string content and encode it safely to UTF-8 bytes
  csv_string = output.getvalue()
  print(csv_string)  # Optional: For debugging purposes, to see the CSV content
  return csv_string.encode("utf-8")


def check_tool_call_limit(tool_context: ToolContext) -> bool:
  print("This is the tool_context state: ", tool_context.state)

  current_invocation = getattr(tool_context, "invocation_id", None)

  # Track the last invocation id where tools were counted
  last_invocation = tool_context.state.get("LAST_INVOCATION_ID")

  if last_invocation != current_invocation:
    # It's a brand new turn/question from the user—reset the counter!
    tool_context.state["TOOL_CALL_COUNT"] = 0
    tool_context.state["LAST_INVOCATION_ID"] = current_invocation

  count = tool_context.state.get("TOOL_CALL_COUNT", 0)

  if count >= MAX_TOOL_CALLS:
    logging.warning("Maximum tool call limit reached.")
    return False

  tool_context.state["TOOL_CALL_COUNT"] = count + 1
  logging.info(f"Tool call {tool_context.state['TOOL_CALL_COUNT']}/{MAX_TOOL_CALLS}")
  return True


def serialize_data(data_list):
  """Safely serializes query results into a JSON string for messaging/state storage."""
  try:
    return json.dumps(data_list, default=str)
  except Exception as e:
    logging.error(f"Serialization failed: {e}")
    return str(data_list)


async def cloudsql_db_agent(user_query: str, tool_context: ToolContext):
  """Executes a natural language query against the Cloud SQL MySQL database.

  This agent translates the user query into a MySQL-compatible SQL statement,
  fetches the records, and handles the output based on the result size:
  - Returns a message if no records are found.
  - Returns the raw data directly if there are 2 or fewer records.
  - Saves the data as a CSV artifact and returns the filename if there are more than 2 records.

  Args:
      user_query (str): The natural language query requesting data from Cloud SQL.
      tool_context (ToolContext): The execution context managing state and tool call limits.

  Returns:
      dict | str: A dictionary containing the success flag, message, and optional data or artifact info,
                  or a string warning if the tool call limit has been exceeded.
  """

  if not check_tool_call_limit(tool_context):
    return "Maximum tool call limit reached. Use the information already collected."

  sql_query = get_cloudsql_sql(user_query)

  logging.info(f"Executing SQL Query for Cloud SQL MySQL: {sql_query}")

  data_list = execute_select_cloudsql(sql_query)

  if len(data_list) == 0:
    return {
        "flag": "Success",
        "Message": "No data found for the given query.",
    }
  elif len(data_list) <= 2:
    return {
        "flag": "Success",
        "Message": f"Data retrieved successfully. Number of records: {len(data_list)}",
        "data": serialize_data(data_list),
    }
  else:
    filename = f"{uuid.uuid4()}.csv"
    df = pd.DataFrame(data_list)
    csv_bytes = df.to_csv(index=False).encode("utf-8")

    csv_artifact = types.Part(
        inline_data=types.Blob(mime_type="text/csv", data=csv_bytes)
    )
    await tool_context.save_artifact(filename=filename, artifact=csv_artifact)

    return {
        "flag": "Success",
        "Message": f"Data is saved as file : {filename}. Please download the file to view the data.",
    }


async def big_query_db_agent(user_query: str, tool_context: ToolContext):
  """Executes a natural language query against the Google BigQuery data warehouse.

  This agent translates the user query into a BigQuery-compatible SQL statement,
  fetches the records, and handles the output based on the result size:
  - Returns a message if no records are found.
  - Returns the raw data directly if there are 2 or fewer records.
  - Saves the data as a CSV artifact and returns the filename if there are more than 2 records.

  Args:
      user_query (str): The natural language query requesting data from BigQuery.
      tool_context (ToolContext): The execution context managing state and tool call limits.

  Returns:
      dict | str: A dictionary containing the success flag, message, and optional data or artifact info,
                  or a string warning if the tool call limit has been exceeded.
  """

  if not check_tool_call_limit(tool_context):
    return "Maximum tool call limit reached. Use the information already collected."

  sql_query = get_big_query_sql(user_query)

  logging.info(f"Executing SQL Query for BigQuery: {sql_query}")

  data_list = execute_select_bigquery(sql_query)

  if len(data_list) == 0:
    return {
        "flag": "Success",
        "Message": "No data found for the given query.",
    }
  elif len(data_list) <= 2:
    return {
        "flag": "Success",
        "Message": f"Data retrieved successfully. Number of records: {len(data_list)}",
        "data": serialize_data(data_list),
    }
  else:
    filename = f"{uuid.uuid4()}.csv"
    df = pd.DataFrame(data_list)
    csv_bytes = df.to_csv(index=False).encode("utf-8")
    
    csv_artifact = types.Part.from_bytes(data=csv_bytes, mime_type="text/csv")
    await tool_context.save_artifact(filename=filename, artifact=csv_artifact)

    return {
        "flag": "Success",
        "Message": f"Data is saved as file : {filename}. Please download the file to view the data.",
    }