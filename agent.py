import logging
import google.cloud.logging
from google.adk.agents import Agent

from .sub_agents.database_analysis_agent.agent import root_agent as db_analysis_agent 
from .sub_agents.stock_analysis_agent.agent import root_agent as stock_agent 
from .sub_agents.database_analysis_agent.llm.llm_provider import model_name

# --- Set up GCP Cloud Logging ---
# Initialize the client. If running on GCP (Vertex AI, Cloud Run, GAE, GKE),
# authentication and project ID are automatically detected.
client = google.cloud.logging.Client()
client.setup_logging()

# Create a dedicated logger for agent telemetry
logger = logging.getLogger("adk_agent_logger")
logger.setLevel(logging.INFO)


# --- Define the Root Agent ---
root_agent = Agent(
    name="manager",
    model=model_name,
    description="Manager agent",
    instruction="""
    You are a manager agent that is responsible for overseeing the work of the other agents.

    Always delegate the task to the appropriate agent. Use your best judgement 
    to determine which agent to delegate to.

    You are responsible for delegating tasks to the following agent:
    - db_analysis_agent
    - stock_agent

    Analyze the user's request carefully:
    - Delegate to **db_analysis_agent** when the user requests quarterly sales data, database records, or Division A/Division B metrics. Keep the queries in simple english, let db_analysis_agent generate the actual queries.
    - Delegate to **stock_agent** when the user requests historical stock prices, date ranges, or percentage change calculations for specific named stocks.
    - If a user request requires both internal database metrics and external stock performance, coordinate the work across both agents to provide a complete answer.
    """,
    sub_agents=[db_analysis_agent, stock_agent],
)


# --- Execution Wrapper with GCP Logging ---
def run_agent_with_logging(user_prompt: str, session_id: str = "default_session"):
    """Executes the root agent while logging prompts and responses directly to GCP."""
    
    # 1. Log incoming user prompt to GCP Cloud Logging
    logger.info(
        "Agent Prompt Received",
        extra={
            "json_fields": {
                "event": "user_prompt",
                "agent_name": root_agent.name,
                "session_id": session_id,
                "prompt": user_prompt,
            }
        }
    )

    try:
        # 2. Run your ADK agent (adjust call method based on your runner/framework implementation)
        response = root_agent.run(user_prompt)  # or runner.run(...)

        # 3. Log generated response to GCP Cloud Logging
        logger.info(
            "Agent Response Generated",
            extra={
                "json_fields": {
                    "event": "agent_response",
                    "agent_name": root_agent.name,
                    "session_id": session_id,
                    "response": str(response),
                }
            }
        )
        return response

    except Exception as e:
        # Log any agent execution errors directly to GCP
        logger.error(
            "Agent Execution Failed",
            extra={
                "json_fields": {
                    "event": "agent_error",
                    "agent_name": root_agent.name,
                    "session_id": session_id,
                    "error": str(e),
                }
            }
        )
        raise e