"""Main AI Agent class that orchestrates natural language processing and Snowflake interactions."""

import pandas as pd
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
from loguru import logger
from rich.console import Console
from rich.table import Table
from rich.syntax import Syntax
from rich.panel import Panel

from .snowflake_client import snowflake_client
from .query_translator import QueryTranslator, QueryContext


@dataclass
class ConversationMessage:
    """Represents a single message in the conversation."""
    timestamp: datetime
    role: str  # 'user' or 'assistant'
    content: str
    query: Optional[str] = None
    results: Optional[Any] = None


@dataclass
class AgentSession:
    """Represents an agent session with conversation history."""
    session_id: str
    created_at: datetime
    messages: List[ConversationMessage] = field(default_factory=list)
    context_cache: Dict[str, Any] = field(default_factory=dict)


class SnowflakeAIAgent:
    """Main AI Agent for interacting with Snowflake using natural language."""
    
    def __init__(self):
        """Initialize the AI Agent."""
        self.translator = QueryTranslator()
        self.console = Console()
        self.current_session = None
        self.database_context = None
        logger.info("Snowflake AI Agent initialized")
    
    def start_session(self, session_id: Optional[str] = None) -> str:
        """
        Start a new conversation session.
        
        Args:
            session_id: Optional session ID, if None a new one will be generated
            
        Returns:
            Session ID
        """
        if not session_id:
            session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        self.current_session = AgentSession(
            session_id=session_id,
            created_at=datetime.now()
        )
        
        logger.info(f"Started new session: {session_id}")
        return session_id
    
    def load_database_context(self, use_cache: bool = True) -> QueryContext:
        """
        Load database schema and sample data for query generation context.
        
        Args:
            use_cache: Whether to use cached context if available
            
        Returns:
            Query context with schema and sample data
        """
        if use_cache and self.database_context:
            return self.database_context
        
        logger.info("Loading database context...")
        
        try:
            # Get list of tables
            tables = snowflake_client.list_tables()
            
            table_schemas = {}
            sample_data = {}
            
            for table in tables[:10]:  # Limit to first 10 tables to avoid overwhelming context
                try:
                    # Get table schema
                    schema_info = snowflake_client.get_table_info(table)
                    table_schemas[table] = schema_info
                    
                    # Get sample data
                    samples = snowflake_client.get_sample_data(table, limit=3)
                    sample_data[table] = samples
                    
                except Exception as e:
                    logger.warning(f"Failed to load context for table {table}: {e}")
                    continue
            
            # Get conversation history for context
            conversation_history = []
            if self.current_session:
                for msg in self.current_session.messages[-5:]:  # Last 5 messages
                    conversation_history.append({
                        "role": msg.role,
                        "content": msg.content
                    })
            
            self.database_context = QueryContext(
                table_schemas=table_schemas,
                sample_data=sample_data,
                conversation_history=conversation_history
            )
            
            logger.info(f"Database context loaded: {len(table_schemas)} tables")
            return self.database_context
            
        except Exception as e:
            logger.error(f"Failed to load database context: {e}")
            raise
    
    def process_query(self, natural_language: str, execute: bool = True) -> Dict[str, Any]:
        """
        Process a natural language query.
        
        Args:
            natural_language: The natural language question
            execute: Whether to execute the generated SQL query
            
        Returns:
            Dictionary containing query, results, and metadata
        """
        if not self.current_session:
            self.start_session()
        
        logger.info(f"Processing query: {natural_language}")
        
        try:
            # Load database context
            context = self.load_database_context()
            
            # Translate to SQL
            sql_query = self.translator.translate_query(natural_language, context)
            
            # Validate query
            validation = self.translator.validate_query(sql_query)
            
            response = {
                "natural_language": natural_language,
                "sql_query": sql_query,
                "validation": validation,
                "executed": False,
                "results": None,
                "error": None,
                "suggestions": self.translator.suggest_improvements(sql_query)
            }
            
            # Execute query if requested and validation passes
            if execute and validation["is_valid"]:
                try:
                    results = snowflake_client.execute_query(sql_query)
                    response["executed"] = True
                    response["results"] = results
                    response["row_count"] = len(results) if results else 0
                    
                except Exception as e:
                    response["error"] = str(e)
                    logger.error(f"Query execution failed: {e}")
            
            # Add to conversation history
            user_message = ConversationMessage(
                timestamp=datetime.now(),
                role="user",
                content=natural_language
            )
            
            assistant_message = ConversationMessage(
                timestamp=datetime.now(),
                role="assistant",
                content=f"Generated SQL query: {sql_query}",
                query=sql_query,
                results=response.get("results")
            )
            
            self.current_session.messages.extend([user_message, assistant_message])
            
            return response
            
        except Exception as e:
            logger.error(f"Query processing failed: {e}")
            return {
                "natural_language": natural_language,
                "error": str(e),
                "executed": False
            }
    
    def display_results(self, response: Dict[str, Any]) -> None:
        """
        Display query results in a formatted way.
        
        Args:
            response: Response from process_query
        """
        self.console.print("\n" + "="*80)
        
        # Display natural language query
        self.console.print(Panel(
            response["natural_language"],
            title="[bold blue]Natural Language Query",
            border_style="blue"
        ))
        
        # Display generated SQL
        if "sql_query" in response:
            sql_syntax = Syntax(response["sql_query"], "sql", theme="monokai", line_numbers=True)
            self.console.print(Panel(
                sql_syntax,
                title="[bold green]Generated SQL",
                border_style="green"
            ))
        
        # Display validation warnings/errors
        if "validation" in response:
            validation = response["validation"]
            if validation["warnings"]:
                self.console.print("[bold yellow]Warnings:[/bold yellow]")
                for warning in validation["warnings"]:
                    self.console.print(f"  ⚠️ {warning}")
            
            if validation["errors"]:
                self.console.print("[bold red]Errors:[/bold red]")
                for error in validation["errors"]:
                    self.console.print(f"  ❌ {error}")
        
        # Display results
        if response.get("executed") and response.get("results"):
            results = response["results"]
            row_count = response.get("row_count", len(results))
            
            self.console.print(f"\n[bold]Results ({row_count} rows):[/bold]")
            
            if results:
                # Create rich table
                table = Table(show_header=True, header_style="bold magenta")
                
                # Add columns
                columns = list(results[0].keys())
                for col in columns:
                    table.add_column(col)
                
                # Add rows (limit to 20 for display)
                for row in results[:20]:
                    table.add_row(*[str(row.get(col, '')) for col in columns])
                
                self.console.print(table)
                
                if len(results) > 20:
                    self.console.print(f"[dim]... showing first 20 of {len(results)} rows[/dim]")
        
        # Display suggestions
        if "suggestions" in response and response["suggestions"]:
            self.console.print("\n[bold cyan]Suggestions for improvement:[/bold cyan]")
            for suggestion in response["suggestions"]:
                self.console.print(f"  💡 {suggestion}")
        
        # Display error if any
        if response.get("error"):
            self.console.print(Panel(
                response["error"],
                title="[bold red]Error",
                border_style="red"
            ))
        
        self.console.print("="*80 + "\n")
    
    def get_session_summary(self) -> Dict[str, Any]:
        """
        Get summary of current session.
        
        Returns:
            Session summary information
        """
        if not self.current_session:
            return {"error": "No active session"}
        
        return {
            "session_id": self.current_session.session_id,
            "created_at": self.current_session.created_at,
            "message_count": len(self.current_session.messages),
            "queries_executed": len([msg for msg in self.current_session.messages if msg.query]),
        }
    
    def export_results_to_csv(self, response: Dict[str, Any], filename: str) -> None:
        """
        Export query results to CSV file.
        
        Args:
            response: Response containing results
            filename: Output filename
        """
        if not response.get("results"):
            logger.warning("No results to export")
            return
        
        df = pd.DataFrame(response["results"])
        df.to_csv(filename, index=False)
        logger.info(f"Results exported to {filename}")
        self.console.print(f"✅ Results exported to {filename}")


# Global agent instance
agent = SnowflakeAIAgent()