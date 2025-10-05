# Snowflake AI Agent

A powerful AI agent that can interact with Snowflake data warehouses using natural language queries. Snowflake helped to organize and make data pipelines. 

## Features

- Natural language to SQL query translation
- Snowflake database connectivity
- Conversation history and context management
- Rich formatting of query results
- Interactive CLI interface

## PipeLine

<img width="4170" height="2970" alt="snowchat_clean_architecture" src="https://github.com/user-attachments/assets/8df57a9c-5a34-4144-b9fb-b7f40d20588f" />


## Setup

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure environment variables:**
   Copy `.env.example` to `.env` and fill in your Snowflake credentials:
   ```
   SNOWFLAKE_ACCOUNT=your_account
   SNOWFLAKE_USER=your_username
   SNOWFLAKE_PASSWORD=your_password
   SNOWFLAKE_WAREHOUSE=your_warehouse
   SNOWFLAKE_DATABASE=your_database
   SNOWFLAKE_SCHEMA=your_schema
   OPENAI_API_KEY=your_openai_key
   ```

3. **Run the agent:**
   ```bash
   python -m src.main
   ```

## Usage

The AI agent can understand natural language queries and convert them to SQL:

- "Show me sales data for the last month"
- "What are the top 10 customers by revenue?"
- "Count the number of orders by region"

## Project Structure

```
snowflake/
├── src/
│   ├── __init__.py
│   ├── main.py
│   ├── agent.py
│   ├── snowflake_client.py
│   └── query_translator.py
├── config/
│   └── settings.py
├── examples/
│   └── example_usage.py
├── tests/
│   └── test_agent.py
├── requirements.txt
├── .env.example
└── README.md
```

## License

MIT License
