import datetime
from google.adk.agents import (
    LlmAgent,
    SequentialAgent,
)

from .agent_tools.agent_tools import (
    calculate_percentage_change,
    get_stock_price_on_dates,
)
from .llm.llm_model import MODEL, llm_model


def get_current_date() -> str:
    """Gets the current date.

    Returns:
        A string containing the current date in YYYY-MM-DD format.
    """
    now = datetime.datetime.now()
    return f"The current date is {now.strftime('%Y-%m-%d')}"


# 1. First Agent: Retrieves current date (if needed) and fetches stock prices
price_retrieval_agent = LlmAgent(
    name="price_retrieval_agent",
    model=MODEL,
    description="An agent that determines the correct dates and fetches stock prices.",
    instruction=(
        "You are a data retrieval specialist. Your goal is to determine the correct start and end dates "
        "and fetch the stock prices.\n"
        "1. **Determine Today's Date**:\n"
        "   - If the user query requires relative date calculations (e.g., 'last 4 months', 'last 12 months', "
        "'today', or no dates specified), call the `get_current_date` tool first to get the current date.\n"
        "2. **Calculate Date Range**:\n"
        "   - If specific dates are provided, use them.\n"
        "   - If no dates are mentioned, default to the last 1 year from the retrieved current date.\n"
        "   - If a relative range is requested (e.g., 'last 4 months', 'last 12 months'), calculate the start date "
        "by subtracting that duration from the retrieved current date.\n"
        "3. **Fetch Stock Prices**:\n"
        "   - Call the `get_stock_price_on_dates` tool using the calculated Start Date and End Date.\n"
        "4. **Handling Market Closures**:\n"
        "   - If a date falls on a weekend/holiday, retry using the nearest available trading day.\n"
        "5. **Strict Communication Rule**:\n"
        "   - Output strictly the raw stock price data and dates retrieved.\n"
        "   - **Do NOT** calculate, estimate, mention, or comment on any percentage change, stock performance, "
        "or trends. All calculations and comments on performance are handled by a downstream agent."
    ),
    tools=[get_current_date, get_stock_price_on_dates],
    output_key="stock_prices",
)

# 2. Second Agent: Calculates the percentage change from the retrieved prices
calculation_agent = LlmAgent(
    name="calculation_agent",
    model=MODEL,
    description=(
        "An agent that calculates the percentage change from stock price data."
    ),
    instruction=(
        "You are a financial calculation specialist. \n"
        "1. Take the stock price data retrieved from the previous step.\n"
        "2. Pass those values directly into the 'calculate_percentage_change' tool.\n"
        "3. Format the final output clearly for the user, showing the percentage change "
        "and relevant details. Do not estimate prices or perform manual percentage calculations; "
        "strictly use and comment on the tool results.\n"
        "STOCK PRICES : {stock_prices}"
    ),
    tools=[calculate_percentage_change],
)

# 3. Combine them into a Sequential Workflow
stock_performance_agent = SequentialAgent(
    name="stock_performance_pipeline",
    sub_agents=[price_retrieval_agent, calculation_agent],
    description=(
        "A sequential workflow that first fetches stock prices and then"
        " calculates their percentage change."
    ),
)

root_agent = stock_performance_agent