import os
import sqlite3
import httpx
from openai import OpenAI


def tool(func):
    """Decorator marking an agent tool function."""
    func.is_tool = True
    return func


class FinanceAgent:
    def __init__(self):
        self.llm = OpenAI(api_key=os.getenv("OPENAI_API_KEY", "sk-mock-key"))
        self.db = sqlite3.connect("portfolio.db")

    @tool
    def query_stock_price(self, ticker: str) -> float:
        """Fetches live stock market prices via HTTP REST API."""
        resp = httpx.get(f"https://api.marketdata.com/v1/quote/{ticker}")
        return resp.json().get("price", 150.0)

    @tool
    def execute_stock_trade(self, ticker: str, quantity: int, action: str) -> str:
        """Executes a stock buy/sell order in portfolio database."""
        cursor = self.db.cursor()
        cursor.execute("INSERT INTO trades (ticker, quantity, action) VALUES (?, ?, ?)", (ticker, quantity, action))
        self.db.commit()
        return f"Order executed: {action} {quantity} shares of {ticker}"

    def run_rebalance_cycle(self):
        print("Evaluating portfolio sentiment via GPT-4o...")
        prompt = "Analyze current market positions and recommend rebalance trades."
        # LLM call simulated / executed
        return self.execute_stock_trade("AAPL", 50, "BUY")


if __name__ == "__main__":
    agent = FinanceAgent()
    agent.run_rebalance_cycle()
