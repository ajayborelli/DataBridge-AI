# DataBridge AI

**MCP-Powered Intelligent Data Analytics Assistant**

DataBridge AI is an AI-powered business analytics assistant that enables users to query enterprise databases using natural language. Built with **Python**, **Streamlit**, **SQLite**, **Google Gemini**, and the **Model Context Protocol (MCP)**, the application converts user questions into secure SQL queries, retrieves data, generates AI-powered insights, and displays interactive visualizations.

---

## Features

- 🔹 Natural Language to SQL Conversion
- 🔹 Google Gemini AI Integration
- 🔹 Model Context Protocol (MCP) Support
- 🔹 SQL Query Validation (SELECT-only)
- 🔹 AI-Generated Business Insights
- 🔹 Interactive Dashboard
- 🔹 Data Explorer
- 🔹 Conversation History
- 🔹 SQLite Database Integration
- 🔹 Secure Query Execution

---

## Tech Stack

- Python
- Streamlit
- SQLite
- Google Gemini API
- Model Context Protocol (MCP)
- Pandas
- Plotly
- SQL

---

## Project Structure

```
DataBridge-AI/
│
├── app.py
├── ai_agent.py
├── database.py
├── mcp_client.py
├── mcp_server.py
├── requirements.txt
├── data/
│   └── business.db
└── README.md
```

---

## Installation

### Clone the repository

```bash
git clone https://github.com/ajayborelli/DataBridge-AI.git
cd DataBridge-AI
```

### Create a virtual environment

```bash
python -m venv venv
```

### Activate the virtual environment

**Windows**

```bash
venv\Scripts\activate
```

**Linux/macOS**

```bash
source venv/bin/activate
```

### Install dependencies

```bash
pip install -r requirements.txt
```

### Configure Environment Variables

Create a `.env` file and add your Google Gemini API key:

```text
GEMINI_API_KEY=your_api_key_here
```

### Run the application

```bash
streamlit run app.py
```

---

## System Workflow

1. User enters a business question in natural language.
2. Google Gemini converts the request into an SQL query.
3. SQL Validator verifies that only SELECT queries are executed.
4. SQLite retrieves the requested data.
5. Gemini generates business insights.
6. Results are displayed through the Streamlit dashboard.

---

## Performance

| Metric | Value |
|---------|------:|
| Accuracy | 98.63% |
| Precision | 100% |
| Recall | 55% |
| F-Measure | 68.76% |
| Specificity | 100% |

---

## Future Enhancements

- Multi-database support (MySQL, PostgreSQL, SQL Server)
- User authentication
- Cloud deployment
- Predictive analytics
- Role-based access control
- Advanced dashboards

---

##  Author

**Ajay Borelli**

GitHub: https://github.com/ajayborelli


## 
This project is intended for academic and educational purposes.