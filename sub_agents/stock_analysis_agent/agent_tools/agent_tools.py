import pandas as pd
import yfinance as yf


def get_stock_price_on_dates(ticker: str, date_one: str, date_two: str):
    """
    Fetches the closing stock price for a given ticker on two specific dates.

    Args:
        ticker (str): The stock ticker symbol (e.g., 'AAPL', 'MSFT').
        date_one (str): The first target date in 'YYYY-MM-DD' format.
        date_two (str): The second target date in 'YYYY-MM-DD' format.

    Returns:
        dict or str: A dictionary mapping the valid ISO date strings to their 
        respective closing price floats, or an error message if the data cannot be fetched.
    """
    dates = sorted([date_one, date_two])
    # Add buffer day because yfinance end date is exclusive
    end_buffer = (pd.to_datetime(dates[1]) + pd.Timedelta(days=1)).strftime('%Y-%m-%d')
    
    try:
        df = yf.download(ticker, start=dates[0], end=end_buffer, progress=False)
        
        if df.empty:
            return f"No data found for {ticker}."

        # Clean the index format to match user input exactly (YYYY-MM-DD)
        df.index = df.index.strftime('%Y-%m-%d')
        
        # Filter for only the two requested dates
        final_df = df.loc[df.index.isin(dates)] 

        start_date = dates[0]
        end_date = dates[1]
        if len(final_df) ==0:
             return f"Error fetching data: Values for both dates are missing"
        elif len(final_df) == 1:
            if start_date in df.index:
                return f"Error fetching data: Value for {end_date} is missing"
            else:
                return f"Error fetching data: Value for {start_date} is missing"
        else:
            # Return only the Close prices to keep the output concise for the agent
            stock_dict =  final_df['Close'].to_dict()
            stock_ticker = list(stock_dict.keys())[0]
            return stock_dict[stock_ticker]
        
    except Exception as e:
        return f"Error fetching data: {str(e)}"

def calculate_percentage_change(price_data):
    """
    Computes the percentage change between two price points across specified dates.

    Args:
        price_data (dict[str, float]): A dictionary containing exactly two entries 
        mapping ISO date strings ('YYYY-MM-DD') to their corresponding price values.
        Example:
            {
                '2025-02-26': 171.93,
                '2026-03-26': 280.92
            }

    Returns:
        str: A formatted percentage increase or decrease string rounded to two decimal places 
        (e.g., '63.39%'), or an error message if the input format is invalid.
    """
    try:
        # Convert dictionary values or pandas series to a simple list of numbers
        if isinstance(price_data, dict):
            values = list(price_data.values())
        else:
            return "The format is not proper"
        
        if len(values) < 2:
            return "Error: Need two price points. One date might be a market holiday."

        initial_val = float(values[0])
        final_val = float(values[-1]) # Use -1 to get the latest date
        
        pct_change = ((final_val - initial_val) / initial_val) * 100
        return f"{round(pct_change, 2)}%"
    
    except Exception as e:
        return f"Error calculating change: {str(e)}"