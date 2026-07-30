import os
import sqlite3
from anthropic import Anthropic


def tool(func):
    return func


class AutonomousSQLAgent:
    """High-risk autonomous SQL and Shell execution agent without human oversight."""

    def __init__(self):
        self.client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY", "mock-key"))
        self.db = sqlite3.connect("production.db")

    @tool
    def execute_raw_shell(self, command: str) -> str:
        """Executes un-sanitized shell commands directly on system host."""
        return os.popen(command).read()

    @tool
    def delete_database_table(self, table_name: str) -> str:
        """Deletes database tables and destroys data."""
        cursor = self.db.cursor()
        cursor.execute(f"DROP TABLE IF EXISTS {table_name}")
        self.db.commit()
        return f"Table {table_name} dropped successfully."

    def run_autonomous_loop(self):
        """Unbounded autonomous loop execution."""
        while True:
            cmd = "ls -la"
            output = self.execute_raw_shell(cmd)
            break


if __name__ == "__main__":
    agent = AutonomousSQLAgent()
    agent.run_autonomous_loop()
