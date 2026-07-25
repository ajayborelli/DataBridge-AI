import asyncio
import sys
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from ai_agent import generate_sql, generate_insight

def extract_text(result):
    texts = []
    for content in result.content:
        if hasattr(content, "text"):
            texts.append(content.text)

    return "\n".join(texts)

async def ask_databridge(
    question,
    conversation_context=""
):
    
    server_params = StdioServerParameters(
        command=sys.executable,
        args=["mcp_server.py"]
    )

    async with stdio_client(server_params) as (read, write):

        async with ClientSession(read, write) as session:

            await session.initialize()

            schema_result = await session.call_tool(
                "get_database_schema",
                arguments={}
            )

            schema = extract_text(schema_result)

            sql_query = generate_sql(
            question,
            schema,
            conversation_context
)

            query_result = await session.call_tool(
                "execute_read_only_query",
                arguments={
                    "query": sql_query
                }
            )

            result_text = extract_text(query_result)

            insight = generate_insight(
                question,
                result_text
            )

            return {
                "sql": sql_query,
                "result": result_text,
                "insight": insight
            }

async def main():

    print("\n==============================")
    print("        DATABRIDGE AI")
    print("==============================")

    question = input(
        "\nAsk a question about your business data: "
    )

    response = await ask_databridge(question)

    print("\nGenerated SQL:")
    print(response["sql"])

    print("\nDatabase Result:")
    print(response["result"])

    print("\nDataBridge AI Answer:")
    print(response["insight"])

if __name__ == "__main__":
    asyncio.run(main())