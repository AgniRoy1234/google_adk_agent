from google.adk.agents import Agent
from google.adk.agents.sequential_agent import SequentialAgent
from .llm.llm_provider import model_name

from .tools.db_agents import big_query_db_agent, cloudsql_db_agent

database_coordinator_agent = Agent(
    name="database_coordinator_agent",
    model=model_name,
    description=(
        "Fetches quarterly sales data or division sales data from Cloud SQL"
        " MySQL and BigQuery based on the user's request."
    ),
    instruction=(
        "You are an intelligent multi-database query planner. "
        "Analyze the user's request carefully to determine which database to query:\n"
        "- **Cloud SQL MySQL (`cloudsql_db_agent`)**: Contains the **quarterly sales data**.\n"
        "- **BigQuery (`big_query_db_agent`)**: Contains the sales data for **Division A** and **Division B**.\n"
        "- If the user requests data spanning both sources, call both tools.\n"
        "Gather all responses and compile them thoroughly."
    ),
    tools=[cloudsql_db_agent, big_query_db_agent],
    output_key=(
        "raw_db_results"
    ),  # Saves output into state["raw_db_results"] for the next agent
)

# --- 2. Formatter Sub-Agent ---
formatter_agent = Agent(
    name="formatter_agent",
    model=model_name,
    description="Transforms raw database retrieval results into a user-friendly format free of jargon.",
    instruction=(
        "You are a friendly customer-facing data presenter. "
        "Review the raw database execution results stored here:\n\n"
        "{raw_db_results}\n\n"
        "Your goals:\n"
        "1. Present the information clearly using simple, plain language.\n"
        "2. Strip out technical database jargon, internal IDs, or complex structural references unless explicitly asked.\n"
        "3. Format lists or key findings cleanly using friendly bullet points or readable tables.\n"
        "4. If a file attachment artifact was generated, clearly inform the user.\n"
        "5. Strictly do not make assumptions about the data; only present what is available in the results. when the data is avaialble only in form of a file, do not make assumptions."
    ),
)


# --- 3. Root Sequential Agent Pipeline ---
root_agent = SequentialAgent(
    name="database_query_pipeline",
    description=(
        "Executes database retrieval first, then formats the results into an"
        " easy-to-read presentation."
    ),
    sub_agents=[database_coordinator_agent, formatter_agent],
)