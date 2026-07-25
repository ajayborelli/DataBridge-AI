import asyncio
import sqlite3

import pandas as pd
import plotly.express as px
import streamlit as st

from mcp_client import ask_databridge
from ai_agent import generate_sql, generate_insight

# ==== PAGE CONFIGURATION ====

st.set_page_config(
    page_title="DataBridge AI",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==== CONFIGURATION ====

DATABASE_PATH = "data/business.db"


# ==== DATABASE FUNCTIONS ====

def get_connection():
    return sqlite3.connect(DATABASE_PATH)

def load_sales_data():
    conn = get_connection()

    try:
        return pd.read_sql_query(
            "SELECT * FROM sales",
            conn
        )
    finally:
        conn.close()

def execute_query(query):

    cleaned_query = query.strip()

    if not cleaned_query.lower().startswith("select"):
        raise ValueError(
            "Only SELECT queries are permitted."
        )

    forbidden = [
        "insert",
        "update",
        "delete",
        "drop",
        "alter",
        "create",
        "truncate",
        "replace"
    ]

    query_lower = cleaned_query.lower()

    for keyword in forbidden:
        if keyword in query_lower:
            raise ValueError(
                "Unsafe SQL operation detected."
            )

    conn = get_connection()

    try:
        return pd.read_sql_query(
            cleaned_query,
            conn
        )
    finally:
        conn.close()

# ==== LOAD DATA ====
df = load_sales_data()

df["order_date"] = pd.to_datetime(
    df["order_date"]
)

# ==== DATABASE SCHEMA FOR AI ====

SCHEMA = """
DATABASE: Business Sales Database

TABLE: sales

COLUMNS:

id INTEGER
Unique transaction identifier.

order_date TEXT
Date when the transaction occurred.

product TEXT
Name of the product.

category TEXT
Product category.

region TEXT
Sales region.

quantity INTEGER
Number of units sold.

unit_price REAL
Price per individual unit.

revenue REAL
Total transaction revenue.

The revenue column already represents:
quantity * unit_price
"""
# ==== SIDEBAR ====

with st.sidebar:

    st.title("📊 DataBridge AI")

    st.caption(
        "Your Intelligent Business Data Analyst"
    )

    st.divider()

    page = st.radio(
        "Workspace",
        [
            "Executive Dashboard",
            "Ask DataBridge",
            "Data Explorer",
            "System Architecture"
        ]
    )

    st.divider()

    st.write("### System Status")

    st.success("● AI Engine Online")
    st.success("● Database Connected")

    st.caption(
        f"{len(df):,} business transactions loaded"
    )

# ==== GLOBAL DATABRIDGE AI HEADER ====

st.title("📊 DataBridge AI")

st.subheader(
    "MCP-Powered Intelligent Data Analytics Assistant"
)

st.caption(
    "Ask questions about your business data using natural language."
)

st.divider()

# ==== EXECUTIVE DASHBOARD ====

if page == "Executive Dashboard":

    st.title("Executive Business Dashboard")

    st.write(
        "A real-time overview of business performance "
        "and key sales indicators."
    )

    st.divider()
    # ==== KEY PERFORMANCE INDICATORS ====

    total_revenue = df["revenue"].sum()
    total_orders = len(df)
    total_units = df["quantity"].sum()
    average_order = df["revenue"].mean()

    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "Total Revenue",
        f"₹{total_revenue:,.0f}"
    )

    col2.metric(
        "Total Orders",
        f"{total_orders:,}"
    )

    col3.metric(
        "Units Sold",
        f"{total_units:,}"
    )

    col4.metric(
        "Average Order Value",
        f"₹{average_order:,.0f}"
    )

    st.divider()
    # ==== BUSINESS LEADERS ====

    product_performance = (
        df.groupby("product")["revenue"]
        .sum()
        .sort_values(
            ascending=False
        )
    )

    region_performance = (
        df.groupby("region")["revenue"]
        .sum()
        .sort_values(
            ascending=False
        )
    )

    category_performance = (
        df.groupby("category")["revenue"]
        .sum()
        .sort_values(
            ascending=False
        )
    )

    col1, col2, col3 = st.columns(3)

    col1.info(
        "🏆 Best Product\n\n"
        f"**{product_performance.index[0]}**\n\n"
        f"₹{product_performance.iloc[0]:,.0f}"
    )

    col2.info(
        "🌍 Best Region\n\n"
        f"**{region_performance.index[0]}**\n\n"
        f"₹{region_performance.iloc[0]:,.0f}"
    )

    col3.info(
        "📦 Best Category\n\n"
        f"**{category_performance.index[0]}**\n\n"
        f"₹{category_performance.iloc[0]:,.0f}"
    )


    st.divider() 
    # ==== MONTHLY TREND ====

    st.subheader(
        "📈 Monthly Revenue Performance"
    )

    monthly = (
        df.set_index("order_date")
        .resample("ME")["revenue"]
        .sum()
        .reset_index()
    )

    monthly["Month"] = (
        monthly["order_date"]
        .dt.strftime("%b %Y")
    )

    figure = px.line(
        monthly,
        x="Month",
        y="revenue",
        markers=True,
        labels={
            "revenue": "Revenue",
            "Month": "Month"
        }
    )

    st.plotly_chart(
        figure,
        use_container_width=True
    )

    # PRODUCT + REGION
    
    col1, col2 = st.columns(2)

    with col1:

        st.subheader(
            "Product Performance"
        )

        product_chart = (
            product_performance
            .reset_index()
        )

        figure = px.bar(
            product_chart,
            x="product",
            y="revenue",
            labels={
                "product": "Product",
                "revenue": "Revenue"
            }
        )

        st.plotly_chart(
            figure,
            use_container_width=True
        )


    with col2:

        st.subheader(
            "Regional Performance"
        )

        region_chart = (
            region_performance
            .reset_index()
        )

        figure = px.pie(
            region_chart,
            names="region",
            values="revenue"
        )

        st.plotly_chart(
            figure,
            use_container_width=True
        )
# ==== ASK DATABRIDGE ====

elif page == "Ask DataBridge":

    st.title("🤖 DataBridge AI Analyst")

    st.caption(
        "Connected to your business database • "
        "Ask questions in natural language • "
        "Follow up on previous analysis"
    )

    st.divider()

    # SESSION STATE

    if "messages" not in st.session_state:
        st.session_state.messages = []

    if "analysis_history" not in st.session_state:
        st.session_state.analysis_history = []

    # ANALYST STATUS BAR

    status1, status2, status3, status4 = st.columns(4)

    status1.metric(
        "Database Records",
        f"{len(df):,}"
    )

    status2.metric(
        "Data Sources",
        "1 Connected"
    )

    status3.metric(
        "AI Analyst",
        "Online"
    )

    status4.metric(
        "Queries This Session",
        len(st.session_state.analysis_history)
    )

    st.divider()
    
    # STARTING SCREEN

    if not st.session_state.messages:

        st.subheader(
            "What would you like to know about your business?"
        )

        st.write(
            "I can analyze revenue, products, regions, "
            "categories, sales trends and business performance."
        )

        col1, col2 = st.columns(2)

        with col1:

            st.info(
                """
**Performance Analysis**

Which products are driving the most revenue?
                """
            )

            st.info(
                """
**Regional Analysis**

Compare sales performance across regions.
                """
            )

        with col2:

            st.info(
                """
**Trend Analysis**

How has revenue changed month by month?
                """
            )

            st.info(
                """
**Executive Analysis**

Give me an overall business performance summary.
                """
            )

    # DISPLAY CONVERSATION HISTORY

    for message in st.session_state.messages:

        with st.chat_message(
            message["role"]
        ):

            st.markdown(
                message["content"]
            )

            if message.get("data") is not None:

                st.dataframe(
                    message["data"],
                    use_container_width=True,
                    hide_index=True
                )

            if message.get("chart") is not None:

                st.plotly_chart(
                    message["chart"],
                    use_container_width=True
                )

            if message.get("sql"):

                with st.expander(
                    "View analysis query"
                ):

                    st.code(
                        message["sql"],
                        language="sql"
                    )
    # REAL CHAT INPUT
    
    question = st.chat_input(
        "Ask anything about your business data..."
    )

    if question:

        # Save user message
        st.session_state.messages.append(
            {
                "role": "user",
                "content": question
            }
        )

        # Display immediately
        with st.chat_message("user"):

            st.markdown(
                question
            )

        # RUN ANALYSIS
        with st.chat_message("assistant"):

            with st.spinner(
                "Analyzing your business data..."
            ):

                try:

                    # Generate SQL
                    sql_query = generate_sql(
                        question,
                        SCHEMA
                    )

                    # Execute SQL
                    result = execute_query(
                        sql_query
                    )

                    if result.empty:

                        insight = (
                            "I analyzed the available business "
                            "data, but no matching records were found."
                        )

                        chart = None

                    else:

                        # Generate AI explanation
                        result_text = result.to_string(
                            index=False
                        )

                        insight = generate_insight(
                            question,
                            result_text
                        )
                        # AUTOMATIC CHART GENERATION

                        chart = None

                        numeric_columns = (
                            result
                            .select_dtypes(
                                include="number"
                            )
                            .columns
                            .tolist()
                        )

                        if (
                            len(result) > 1
                            and numeric_columns
                        ):

                            label_column = (
                                result.columns[0]
                            )

                            value_column = (
                                numeric_columns[-1]
                            )

                            # Line chart for time-based data
                            if any(
                                word in question.lower()
                                for word in [
                                    "month",
                                    "trend",
                                    "time",
                                    "year"
                                ]
                            ):

                                chart = px.line(
                                    result,
                                    x=label_column,
                                    y=value_column,
                                    markers=True
                                )

                            # Pie chart for distribution
                            elif any(
                                word in question.lower()
                                for word in [
                                    "percentage",
                                    "share",
                                    "distribution"
                                ]
                            ):

                                chart = px.pie(
                                    result,
                                    names=label_column,
                                    values=value_column
                                )

                            # Default analytical chart
                            else:

                                chart = px.bar(
                                    result,
                                    x=label_column,
                                    y=value_column
                                )

                    # DISPLAY RESPONSE

                    st.markdown(
                        insight
                    )

                    if not result.empty:

                        with st.expander(
                            "📊 View supporting data",
                            expanded=False
                        ):

                            st.dataframe(
                                result,
                                use_container_width=True,
                                hide_index=True
                            )

                    if chart is not None:

                        st.plotly_chart(
                            chart,
                            use_container_width=True
                        )

                    with st.expander(
                        "🔍 Analysis transparency"
                    ):

                        st.caption(
                            "SQL generated by DataBridge AI"
                        )

                        st.code(
                            sql_query,
                            language="sql"
                        )

                    # SAVE ASSISTANT RESPONSE

                    st.session_state.messages.append(
                        {
                            "role": "assistant",
                            "content": insight,
                            "data": result,
                            "chart": chart,
                            "sql": sql_query
                        }
                    )

                    st.session_state.analysis_history.append(
                        {
                            "question": question,
                            "sql": sql_query
                        }
                    )

                except Exception as error:

                    error_message = (
                        "I couldn't complete that analysis. "
                        f"Technical details: {error}"
                    )

                    st.error(
                        error_message
                    )

    # CLEAR SESSION

    if st.session_state.messages:

        st.divider()

        if st.button(
            "🗑️ Start New Analysis Session"
        ):

            st.session_state.messages = []
            st.session_state.analysis_history = []

            st.rerun()
            
# DATA EXPLORER

elif page == "Data Explorer":

    st.title(
        "🔎 Business Data Explorer"
    )

    st.write(
        "Explore and filter the underlying "
        "business transaction data."
    )

    st.divider()

    col1, col2, col3 = st.columns(3)

    selected_regions = col1.multiselect(
        "Region",
        sorted(
            df["region"].unique()
        )
    )

    selected_categories = col2.multiselect(
        "Category",
        sorted(
            df["category"].unique()
        )
    )

    selected_products = col3.multiselect(
        "Product",
        sorted(
            df["product"].unique()
        )
    )

    filtered_df = df.copy()

    if selected_regions:

        filtered_df = filtered_df[
            filtered_df["region"].isin(
                selected_regions
            )
        ]

    if selected_categories:

        filtered_df = filtered_df[
            filtered_df["category"].isin(
                selected_categories
            )
        ]

    if selected_products:

        filtered_df = filtered_df[
            filtered_df["product"].isin(
                selected_products
            )
        ]


    st.write(
        f"Showing **{len(filtered_df):,}** transactions"
    )

    st.dataframe(
        filtered_df,
        use_container_width=True,
        hide_index=True
    )

    csv = filtered_df.to_csv(
        index=False
    )

    st.download_button(
        "⬇️ Export Filtered Data",
        csv,
        "databridge_business_data.csv",
        "text/csv"
    )

# SYSTEM ARCHITECTURE

elif page == "System Architecture":

    st.title(
        "⚙️ DataBridge AI Architecture"
    )

    st.write(
        "DataBridge AI bridges the gap between "
        "non-technical business users and structured data."
    )

    st.divider()

    st.subheader(
        "How DataBridge Works"
    )

    st.markdown(
        """
### 1. Natural Language Question

The business user asks a question without writing SQL.

⬇️

### 2. AI Query Understanding

The AI understands the business intent and database structure.

⬇️

### 3. Dynamic SQL Generation

The question is automatically converted into a read-only SQL query.

⬇️

### 4. Query Security Validation

DataBridge permits only analytical `SELECT` operations.

⬇️

### 5. Business Database Analysis

The generated query is executed against the SQLite business database.

⬇️

### 6. AI Business Interpretation

Raw query results are converted into understandable business insights.

⬇️

### 7. Intelligent Presentation

The user receives:

- Executive insights
- Data tables
- Dynamic visualizations
- Transparent SQL analysis
        """
    )

    st.divider()

    st.subheader(
        "Technology Stack"
    )

    col1, col2, col3 = st.columns(3)

    col1.info(
        """
### AI Layer

Gemini API

Natural Language Processing

Text-to-SQL Generation

Business Insight Generation
        """
    )

    col2.info(
        """
### Data Layer

SQLite

SQL

Pandas

Secure Read-Only Queries
        """
    )

    col3.info(
        """
### Application Layer

Python

Streamlit

Plotly

MCP Integration Module
        """
    )
st.title("📊 DataBridge AI")

st.subheader(
    "MCP-Powered Intelligent Data Analytics Assistant"
)

st.write(
    "Ask questions about your business data using natural language."
)

st.divider()

questions = [
        "Ask your own question...",
        "Which product generated the highest total revenue?",
        "What is the total revenue?",
        "Which region generated the highest revenue?",
        "Which category performed the best?",
        "Show the top 5 products by revenue.",
        "Compare revenue across all regions.",
        "Which month generated the highest revenue?",
        "What is the average order value?",
        "Which product sold the most units?",
        "Show the monthly revenue trend.",
        "Give me an overall business performance summary."
    ]

selected_question = st.selectbox(
        "Ask a question",
        questions
    )

if selected_question == "Ask your own question...":
        question = st.text_input(
            "Type your question",
            placeholder="What would you like to know about your business?"
        )
else:
        question = selected_question

if st.button("Analyze Data", type="primary"):

    if not question.strip():

        st.warning(
            "Please enter a question."
        )

    else:

        try:

            with st.spinner(
                "DataBridge AI is analyzing your data..."
            ):

                # Build context from previous questions
                previous_questions = [
                    message["content"]
                    for message in st.session_state.get(
                        "messages",
                        []
                    )
                    if message.get("role") == "user"
                ]

                conversation_context = "\n".join(
                    previous_questions[-5:]
                )

                response = asyncio.run(
                    ask_databridge(
                        question,
                        conversation_context
                    )
                )

            st.success(
                "Analysis completed successfully!"
            )


            st.subheader(
                "🤖 AI Business Insight"
            )

            st.write(
                response["insight"]
            )


            st.subheader(
                "📊 Database Result"
            )

            st.code(
                response["result"]
            )

            with st.expander(
                "🔍 View Generated SQL"
            ):

                st.code(
                    response["sql"],
                    language="sql"
                )

        except Exception as error:

            st.error(
                f"Error: {error}"
            )
# PROFESSIONAL RESPONSIVE UI STYLING

st.markdown("""
<style>

/* ---------------------------------------------------------
   MAIN APPLICATION
--------------------------------------------------------- */

.stApp {
    background:
        radial-gradient(circle at 10% 10%, rgba(45, 100, 255, 0.08), transparent 30%),
        radial-gradient(circle at 90% 20%, rgba(124, 58, 237, 0.07), transparent 30%),
        #0b0f17;
}

/* Main content width */

.block-container {
    max-width: 1450px;
    padding-top: 3rem;
    padding-bottom: 4rem;
    padding-left: 3rem;
    padding-right: 3rem;
}

/* ---------------------------------------------------------
   TYPOGRAPHY
--------------------------------------------------------- */

h1 {
    font-weight: 800 !important;
    letter-spacing: -1.5px !important;
}

h2, h3 {
    font-weight: 700 !important;
}

p {
    line-height: 1.7;
}

/* ---------------------------------------------------------
   SIDEBAR
--------------------------------------------------------- */

[data-testid="stSidebar"] {
    background:
        linear-gradient(
            180deg,
            #151a27 0%,
            #10141f 100%
        );

    border-right: 1px solid rgba(255,255,255,0.08);
}

[data-testid="stSidebar"] > div:first-child {
    padding-top: 2rem;
}

/* Sidebar radio navigation */

[data-testid="stSidebar"] label {
    transition: all 0.2s ease;
}

/* ---------------------------------------------------------
   METRIC CARDS
--------------------------------------------------------- */

[data-testid="stMetric"] {

    background:
        linear-gradient(
            145deg,
            rgba(30, 41, 59, 0.85),
            rgba(17, 24, 39, 0.9)
        );

    border:
        1px solid rgba(255,255,255,0.08);

    border-radius: 18px;

    padding: 22px;

    min-height: 125px;

    box-shadow:
        0 8px 30px rgba(0,0,0,0.20);

    transition:
        transform 0.25s ease,
        border 0.25s ease,
        box-shadow 0.25s ease;
}

[data-testid="stMetric"]:hover {

    transform: translateY(-4px);

    border:
        1px solid rgba(59,130,246,0.40);

    box-shadow:
        0 15px 40px rgba(0,0,0,0.30);
}

/* Metric label */

[data-testid="stMetricLabel"] {

    font-size: 14px;

    opacity: 0.75;
}

/* Metric value */

[data-testid="stMetricValue"] {

    font-weight: 700;

    letter-spacing: -1px;
}

/* ---------------------------------------------------------
   INFO / STATUS CARDS
--------------------------------------------------------- */

[data-testid="stAlert"] {

    border-radius: 16px;

    border:
        1px solid rgba(255,255,255,0.08);

    box-shadow:
        0 8px 25px rgba(0,0,0,0.15);

    transition:
        transform 0.2s ease;
}

[data-testid="stAlert"]:hover {

    transform: translateY(-2px);
}

/* ---------------------------------------------------------
   BUTTONS
--------------------------------------------------------- */

.stButton > button {

    border-radius: 12px;

    font-weight: 600;

    min-height: 46px;

    transition:
        transform 0.2s ease,
        box-shadow 0.2s ease;
}

.stButton > button:hover {

    transform: translateY(-2px);

    box-shadow:
        0 8px 25px rgba(59,130,246,0.25);
}

/* ---------------------------------------------------------
   INPUT FIELDS
--------------------------------------------------------- */

[data-baseweb="input"] {

    border-radius: 12px !important;
}

[data-baseweb="select"] > div {

    border-radius: 12px !important;
}

textarea {

    border-radius: 12px !important;
}

/* Chat input */

[data-testid="stChatInput"] {

    border-radius: 16px;

    box-shadow:
        0 8px 30px rgba(0,0,0,0.25);
}

/* ---------------------------------------------------------
   DATAFRAMES
--------------------------------------------------------- */

[data-testid="stDataFrame"] {

    border-radius: 16px;

    overflow: hidden;

    border:
        1px solid rgba(255,255,255,0.08);
}

/* ---------------------------------------------------------
   PLOTLY CHARTS
--------------------------------------------------------- */

[data-testid="stPlotlyChart"] {

    background:
        rgba(17,24,39,0.45);

    border:
        1px solid rgba(255,255,255,0.07);

    border-radius: 18px;

    padding: 10px;

    box-shadow:
        0 10px 35px rgba(0,0,0,0.18);
}


/* ---------------------------------------------------------
   EXPANDERS
--------------------------------------------------------- */

[data-testid="stExpander"] {

    border-radius: 14px !important;

    border:
        1px solid rgba(255,255,255,0.08) !important;

    overflow: hidden;
}


/* ---------------------------------------------------------
   DIVIDERS
--------------------------------------------------------- */

hr {

    border-color:
        rgba(255,255,255,0.08) !important;

    margin-top: 2rem !important;

    margin-bottom: 2rem !important;
}


/* ---------------------------------------------------------
   SCROLLBAR
--------------------------------------------------------- */

::-webkit-scrollbar {

    width: 8px;
}


::-webkit-scrollbar-track {

    background: #0b0f17;
}


::-webkit-scrollbar-thumb {

    background: #374151;

    border-radius: 10px;
}


::-webkit-scrollbar-thumb:hover {

    background: #4b5563;
}


/* ---------------------------------------------------------
   RESPONSIVE TABLET
--------------------------------------------------------- */

@media screen and (max-width: 1000px) {

    .block-container {

        padding-left: 1.5rem;

        padding-right: 1.5rem;

        padding-top: 2rem;
    }


    h1 {

        font-size: 2.2rem !important;
    }


    [data-testid="stMetric"] {

        padding: 16px;

        min-height: 105px;
    }
}


/* ---------------------------------------------------------
   RESPONSIVE MOBILE
--------------------------------------------------------- */

@media screen and (max-width: 650px) {

    .block-container {

        padding-left: 1rem;

        padding-right: 1rem;

        padding-top: 1.5rem;
    }


    h1 {

        font-size: 1.8rem !important;

        letter-spacing: -0.5px !important;
    }


    h2 {

        font-size: 1.4rem !important;
    }


    [data-testid="stMetric"] {

        padding: 14px;

        border-radius: 14px;

        min-height: auto;
    }


    [data-testid="stMetricValue"] {

        font-size: 1.6rem !important;
    }


    [data-testid="stPlotlyChart"] {

        border-radius: 12px;

        padding: 4px;
    }
}

</style>
""", unsafe_allow_html=True)