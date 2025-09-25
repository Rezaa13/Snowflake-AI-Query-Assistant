"""Natural language to SQL query translator using OpenAI GPT models."""

import openai
from typing import List, Dict, Any, Optional
from loguru import logger
from dataclasses import dataclass

from config.settings import ai_settings


@dataclass
class QueryContext:
    """Context information for query generation."""
    table_schemas: Dict[str, List[Dict[str, Any]]]
    sample_data: Dict[str, List[Dict[str, Any]]]
    conversation_history: List[Dict[str, str]]


class QueryTranslator:
    """Translates natural language queries to SQL using OpenAI GPT."""
    
    def __init__(self):
        """Initialize the query translator."""
        openai.api_key = ai_settings.openai_api_key
        self.model = ai_settings.model
        self.temperature = ai_settings.temperature
        self.max_tokens = ai_settings.max_tokens
    
    def create_system_prompt(self, context: QueryContext) -> str:
        """
        Create the system prompt with database schema information.
        
        Args:
            context: Query context containing schema and sample data
            
        Returns:
            System prompt string
        """
        prompt = """You are an expert SQL query generator for Snowflake data warehouse. 
Your task is to convert natural language questions into accurate SQL queries.

IMPORTANT GUIDELINES:
1. Always use proper Snowflake SQL syntax
2. Use uppercase for SQL keywords (SELECT, FROM, WHERE, etc.)
3. Use appropriate data types and functions
4. Consider performance - use LIMIT when appropriate
5. Handle date/time functions correctly for Snowflake
6. Use proper JOIN syntax when multiple tables are involved
7. Return ONLY the SQL query, no explanations unless asked

DATABASE SCHEMA:
"""
        
        # Add table schema information
        for table_name, columns in context.table_schemas.items():
            prompt += f"\nTable: {table_name}\n"
            prompt += "Columns:\n"
            for col in columns:
                prompt += f"  - {col['COLUMN_NAME']} ({col['DATA_TYPE']}) - {col.get('COMMENT', 'No description')}\n"
        
        # Add sample data if available
        if context.sample_data:
            prompt += "\nSAMPLE DATA:\n"
            for table_name, samples in context.sample_data.items():
                if samples:
                    prompt += f"\nTable {table_name} sample:\n"
                    # Show first sample row as example
                    sample_row = samples[0]
                    for key, value in sample_row.items():
                        prompt += f"  {key}: {value}\n"
        
        prompt += "\nGenerate SQL queries that are optimized for Snowflake and follow best practices."
        
        return prompt
    
    def translate_query(self, 
                       natural_language: str, 
                       context: QueryContext,
                       include_explanation: bool = False) -> str:
        """
        Translate natural language to SQL query.
        
        Args:
            natural_language: The natural language question
            context: Query context with schema information
            include_explanation: Whether to include explanation
            
        Returns:
            Generated SQL query
        """
        try:
            system_prompt = self.create_system_prompt(context)
            
            messages = [
                {"role": "system", "content": system_prompt},
            ]
            
            # Add conversation history if available
            for msg in context.conversation_history[-5:]:  # Last 5 messages for context
                messages.append(msg)
            
            # Add current question
            user_prompt = natural_language
            if include_explanation:
                user_prompt += "\n\nPlease also provide a brief explanation of what the query does."
            
            messages.append({"role": "user", "content": user_prompt})
            
            logger.info(f"Translating query: {natural_language[:100]}...")
            
            response = openai.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=self.temperature,
                max_tokens=self.max_tokens
            )
            
            sql_query = response.choices[0].message.content.strip()
            
            # Clean up the response - remove markdown formatting if present
            if sql_query.startswith("```sql"):
                sql_query = sql_query[6:]
            if sql_query.endswith("```"):
                sql_query = sql_query[:-3]
            sql_query = sql_query.strip()
            
            logger.info("Query translation completed successfully")
            return sql_query
            
        except Exception as e:
            logger.error(f"Query translation failed: {e}")
            raise
    
    def validate_query(self, sql_query: str) -> Dict[str, Any]:
        """
        Validate the generated SQL query.
        
        Args:
            sql_query: The SQL query to validate
            
        Returns:
            Validation results
        """
        validation_result = {
            "is_valid": True,
            "warnings": [],
            "errors": []
        }
        
        # Basic validation checks
        sql_upper = sql_query.upper()
        
        # Check for potentially dangerous operations
        dangerous_keywords = ["DROP", "DELETE", "TRUNCATE", "ALTER", "CREATE"]
        for keyword in dangerous_keywords:
            if keyword in sql_upper:
                validation_result["warnings"].append(f"Query contains potentially dangerous operation: {keyword}")
        
        # Check for SELECT statement
        if not sql_upper.strip().startswith("SELECT"):
            if not any(keyword in sql_upper for keyword in ["WITH", "SHOW", "DESCRIBE"]):
                validation_result["errors"].append("Query should start with SELECT, WITH, SHOW, or DESCRIBE")
                validation_result["is_valid"] = False
        
        # Check for basic SQL structure
        if "SELECT" in sql_upper and "FROM" not in sql_upper:
            # Allow SELECT without FROM for simple calculations
            if not any(func in sql_upper for func in ["CURRENT_", "SYSDATE", "GETDATE"]):
                validation_result["warnings"].append("SELECT query without FROM clause")
        
        return validation_result
    
    def suggest_improvements(self, sql_query: str) -> List[str]:
        """
        Suggest improvements for the SQL query.
        
        Args:
            sql_query: The SQL query to analyze
            
        Returns:
            List of improvement suggestions
        """
        suggestions = []
        sql_upper = sql_query.upper()
        
        # Check for LIMIT clause
        if "SELECT" in sql_upper and "LIMIT" not in sql_upper:
            suggestions.append("Consider adding LIMIT clause to prevent large result sets")
        
        # Check for WHERE clause
        if "FROM" in sql_upper and "WHERE" not in sql_upper and "GROUP BY" not in sql_upper:
            suggestions.append("Consider adding WHERE clause to filter results")
        
        # Check for proper indexing hints
        if "JOIN" in sql_upper:
            suggestions.append("Ensure JOIN conditions use indexed columns for better performance")
        
        # Check for SELECT *
        if "SELECT *" in sql_upper:
            suggestions.append("Consider selecting specific columns instead of SELECT * for better performance")
        
        return suggestions