import sqlite3
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("DataBridge AI")

DATABASE_PATH = "data/business.db"
def get_connection():
    """Create a connection to the business database."""
    return sqlite3.connect(DATABASE_PATH)
@mcp.tool()
def get_database_schema() -> str:
    """Returns the structure of the sales table."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("PRAGMA table_info(sales)")
    columns = cursor.fetchall()

    conn.close()

    schema = "Sales Table Schema:\n"

    for column in columns:
        schema += f"- {column[1]} ({column[2]})\n"

    return schema

@mcp.tool()
def get_sales_summary() -> str:
    """Returns an overall summary of business sales."""

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            COUNT(*) AS total_orders,
            SUM(quantity) AS total_units,
            SUM(revenue) AS total_revenue,
            AVG(revenue) AS average_order_value
        FROM sales
    """)

    result = cursor.fetchone()
    conn.close()

    return (
        f"Total Orders: {result[0]}\n"
        f"Total Units Sold: {result[1]}\n"
        f"Total Revenue: ₹{result[2]:,.2f}\n"
        f"Average Order Value: ₹{result[3]:,.2f}"
    )

@mcp.tool()
def execute_read_only_query(query: str) -> str:
    """
    Executes a read-only SQL SELECT query.

    Only SELECT statements are permitted.
    """
    
    cleaned_query = query.strip()

    if not cleaned_query.lower().startswith("select"):
        return "Error: Only SELECT queries are allowed."

    forbidden_keywords = [
        "insert",
        "update",
        "delete",
        "drop",
        "alter",
        "create",
        "replace",
        "truncate"
    ]

    query_lower = cleaned_query.lower()

    for keyword in forbidden_keywords:
        if keyword in query_lower:
            return f"Error: '{keyword.upper()}' operations are not allowed."

    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(cleaned_query)

        columns = [
            description[0]
            for description in cursor.description
        ]

        rows = cursor.fetchall()

        conn.close()

        if not rows:
            return "Query executed successfully, but no records were found."

        result = " | ".join(columns) + "\n"
        result += "-" * 60 + "\n"

        for row in rows[:100]:
            result += " | ".join(
                str(value) for value in row
            ) + "\n"

        if len(rows) > 100:
            result += f"\nShowing first 100 of {len(rows)} rows."

        return result

    except sqlite3.Error as error:
        return f"Database error: {error}"

if __name__ == "__main__":
    mcp.run()