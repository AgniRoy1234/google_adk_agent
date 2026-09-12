from google.adk.agents import Agent
from google.adk.tools.agent_tool import AgentTool

from .sub_agents.database_analysis_agent.agent import root_agent as db_analysis_agent 
from .sub_agents.stock_analysis_agent.agent import root_agent as stock_agent 
from .sub_agents.database_analysis_agent.llm.llm_provider import  model_name


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