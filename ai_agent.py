import os
import time
from pathlib import Path

from dotenv import load_dotenv
from google import genai

# LOAD API KEY
BASE_DIR = Path(__file__).resolve().parent
ENV_FILE = BASE_DIR / ".env"

load_dotenv(dotenv_path=ENV_FILE, override=True)

API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    raise ValueError(
        "GEMINI_API_KEY was not found in the .env file."
    )

# CREATE GEMINI CLIENT
client = genai.Client(api_key=API_KEY)

# AVAILABLE GEMINI MODELS
MODELS = [
    "gemini-3.5-flash",
    "gemini-flash-latest",
    "gemini-flash-lite-latest",
]

# GEMINI CALL WITH AUTOMATIC FALLBACK

def call_gemini(prompt):

    last_error = None

    for model in MODELS:

        for attempt in range(2):

            try:
                response = client.models.generate_content(
                    model=model,
                    contents=prompt
                )

                if response.text:
                    return response.text.strip()

            except Exception as error:

                last_error = error

                if attempt == 0:
                    time.sleep(2)

    raise RuntimeError(
        "AI service is temporarily unavailable. "
        f"Last error: {last_error}"
    )

# GENERATE SQL WITH CONVERSATION CONTEXT
def generate_sql(
    question,
    schema,
    conversation_context=""
):

    prompt = f"""
You are the SQL analysis engine of DataBridge AI.

Your task is to convert a business user's natural-language
question into exactly one valid SQLite SELECT query.

DATABASE SCHEMA:

{schema}

PREVIOUS CONVERSATION:

{
    conversation_context
    if conversation_context
    else "No previous conversation."
}

CURRENT USER QUESTION:

{question}

CONTEXT RULES:

1. Understand the current question using previous conversation
   context when necessary.

2. Resolve follow-up questions such as:
   - What about the second highest?
   - Compare it with the previous one.
   - What about the South region?
   - Show me the top 5 instead.
   - Now show this month by month.

3. Always generate a complete standalone SQL query.

4. Previous conversation is context only.
   Database results remain the source of truth.


STRICT SQL RULES:

1. Return ONLY the SQL query.

2. Generate exactly one SELECT query.

3. Never generate:
   INSERT
   UPDATE
   DELETE
   DROP
   ALTER
   CREATE
   REPLACE
   TRUNCATE

4. Use only tables and columns available
   in the provided database schema.

5. Generate SQLite-compatible syntax.

6. Use aggregation functions such as:
   SUM
   AVG
   COUNT
   MIN
   MAX
   when required.

7. Use GROUP BY when comparing:
   products
   categories
   regions
   or time periods.

8. Use ORDER BY and LIMIT for questions
   involving:
   highest
   lowest
   best
   worst
   top results.

9. Do not include explanations.

10. Do not include markdown code blocks.


SQL QUERY:
"""

    sql_query = call_gemini(prompt)

    # Clean accidental markdown
    sql_query = sql_query.replace(
        "```sql",
        ""
    )

    sql_query = sql_query.replace(
        "```SQL",
        ""
    )

    sql_query = sql_query.replace(
        "```",
        ""
    )

    sql_query = sql_query.strip()

    # Remove trailing semicolon
    validation_query = (
        sql_query
        .rstrip(";")
        .strip()
    )

    # SQL SECURITY VALIDATION

    if not validation_query.lower().startswith(
        "select"
    ):
        raise ValueError(
            "AI generated an unsafe query. "
            "Only SELECT queries are allowed."
        )

    forbidden_operations = [
        " insert ",
        " update ",
        " delete ",
        " drop ",
        " alter ",
        " create ",
        " replace ",
        " truncate "
    ]

    normalized_query = (
        f" {validation_query.lower()} "
    )

    for operation in forbidden_operations:

        if operation in normalized_query:

            raise ValueError(
                "Unsafe SQL operation detected."
            )


    return validation_query

# GENERATE BUSINESS INSIGHT
def generate_insight(
    question,
    query_result
):

    prompt = f"""
You are DataBridge AI, an intelligent business
data analytics assistant.

The business user asked:

{question}

The company's database returned:

{query_result}

Provide a clear business analysis.

RULES:

1. Directly answer the user's question.

2. Use ONLY information contained
   in the database result.

3. Never invent numbers.

4. Never invent products,
   regions or categories.

5. Highlight the most important
   business finding.

6. Format monetary values clearly
   when applicable.

7. Keep the explanation professional
   and easy to understand.

8. Do not mention SQL unless necessary.

9. Do not claim information that
   cannot be determined from the result.

BUSINESS INSIGHT:
"""

    return call_gemini(prompt)