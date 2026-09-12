from pydantic import BaseModel, Field

class StockDataOutput(BaseModel):
    stock_name: str = Field(
        ..., 
        description="The ticker symbol or name of the stock."
    )
    start_date: str = Field(
        ..., 
        description="The start date of the period in YYYY-MM-DD format."
    )
    end_date: str = Field(
        ..., 
        description="The end date of the period in YYYY-MM-DD format."
    )
    price_change_percentage: float = Field(
        ..., 
        description="The percentage change in the stock's price over the specified period."
    )