"""Example usage of the Snowflake AI Agent."""

import os
import sys
from pathlib import Path

# Add src to path for imports
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

from agent import agent
from snowflake_client import snowflake_client
from conversation_manager import conversation_manager
from rich.console import Console

console = Console()


def example_basic_usage():
    """Example of basic AI agent usage."""
    console.print("[bold blue]Example 1: Basic Usage[/bold blue]")
    
    # Start a session
    session_id = agent.start_session("example_basic")
    console.print(f"Started session: {session_id}")
    
    # Example queries
    example_queries = [
        "Show me all tables in the database",
        "What are the column names in the customers table?",
        "Count the total number of orders",
        "Show me the top 5 customers by total order value"
    ]
    
    for query in example_queries:
        console.print(f"\n[cyan]Query: {query}[/cyan]")
        response = agent.process_query(query, execute=False)  # Don't execute, just translate
        
        if "sql_query" in response:
            console.print(f"[green]Generated SQL:[/green] {response['sql_query']}")
        
        if response.get("error"):
            console.print(f"[red]Error:[/red] {response['error']}")


def example_with_execution():
    """Example with actual query execution (requires valid Snowflake connection)."""
    console.print("\n[bold blue]Example 2: With Query Execution[/bold blue]")
    
    # Test connection first
    console.print("Testing connection...")
    try:
        if not snowflake_client.test_connection():
            console.print("[yellow]Skipping execution example - no valid connection[/yellow]")
            return
    except Exception as e:
        console.print(f"[yellow]Skipping execution example - connection error: {e}[/yellow]")
        return
    
    # Start session and execute queries
    session_id = agent.start_session("example_execution")
    
    # Simple queries that should work on most Snowflake instances
    safe_queries = [
        "SELECT CURRENT_VERSION()",
        "SELECT CURRENT_DATABASE()",
        "SELECT CURRENT_TIMESTAMP()"
    ]
    
    for query in safe_queries:
        console.print(f"\n[cyan]Query: {query}[/cyan]")
        response = agent.process_query(f"Please run this query: {query}", execute=True)
        agent.display_results(response)


def example_conversation_flow():
    """Example of a conversation flow with follow-up questions."""
    console.print("\n[bold blue]Example 3: Conversation Flow[/bold blue]")
    
    session_id = agent.start_session("example_conversation")
    
    # Simulate a conversation flow
    conversation = [
        "What tables do we have in the database?",
        "Tell me about the customers table structure",
        "Show me a sample of data from the customers table",
        "How many customers do we have in total?"
    ]
    
    for i, query in enumerate(conversation, 1):
        console.print(f"\n[cyan]Step {i}: {query}[/cyan]")
        response = agent.process_query(query, execute=False)
        
        if "sql_query" in response:
            console.print(f"[green]Generated SQL:[/green] {response['sql_query']}")


def example_session_management():
    """Example of session management features."""
    console.print("\n[bold blue]Example 4: Session Management[/bold blue]")
    
    # Create and save a session
    session_id = agent.start_session("example_session_mgmt")
    
    # Add some conversation
    agent.process_query("Show me the database version", execute=False)
    agent.process_query("List all tables", execute=False)
    
    # Save the session
    saved_path = conversation_manager.save_session(agent.current_session)
    console.print(f"Session saved to: {saved_path}")
    
    # List all sessions
    sessions = conversation_manager.list_sessions()
    console.print(f"Found {len(sessions)} sessions:")
    for session in sessions[:3]:  # Show first 3
        console.print(f"  - {session['session_id']} ({session['message_count']} messages)")
    
    # Export session to different formats
    console.print("\nExporting session...")
    txt_export = conversation_manager.export_session(session_id, "txt")
    if txt_export:
        console.print(f"Exported to text: {txt_export}")


def example_error_handling():
    """Example of error handling and validation."""
    console.print("\n[bold blue]Example 5: Error Handling[/bold blue]")
    
    session_id = agent.start_session("example_errors")
    
    # Examples of problematic queries
    problematic_queries = [
        "DELETE FROM customers",  # Dangerous operation
        "This is not a question about data",  # Not a data query
        "Show me data from nonexistent_table"  # Table doesn't exist
    ]
    
    for query in problematic_queries:
        console.print(f"\n[cyan]Problematic Query: {query}[/cyan]")
        response = agent.process_query(query, execute=False)
        
        # Check validation results
        if "validation" in response:
            validation = response["validation"]
            if validation["warnings"]:
                console.print("[yellow]Warnings:[/yellow]")
                for warning in validation["warnings"]:
                    console.print(f"  ⚠️ {warning}")
            
            if validation["errors"]:
                console.print("[red]Errors:[/red]")
                for error in validation["errors"]:
                    console.print(f"  ❌ {error}")
        
        if "suggestions" in response:
            console.print("[blue]Suggestions:[/blue]")
            for suggestion in response["suggestions"]:
                console.print(f"  💡 {suggestion}")


def example_programmatic_usage():
    """Example of using the agent programmatically in your own code."""
    console.print("\n[bold blue]Example 6: Programmatic Usage[/bold blue]")
    
    # This shows how to use the agent in your own Python applications
    
    # Initialize and configure
    session_id = agent.start_session("programmatic_example")
    
    # Process multiple queries and collect results
    queries = [
        "Count all records in each table",
        "Show me tables with more than 1000 records",
        "What's the most recent data timestamp across all tables?"
    ]
    
    results = []
    for query in queries:
        response = agent.process_query(query, execute=False)
        results.append({
            "query": query,
            "sql": response.get("sql_query"),
            "valid": response.get("validation", {}).get("is_valid", False),
            "suggestions": response.get("suggestions", [])
        })
    
    # Process results
    console.print("Processing results programmatically:")
    for result in results:
        console.print(f"Query: {result['query']}")
        console.print(f"Valid: {result['valid']}")
        if result['suggestions']:
            console.print(f"Suggestions: {len(result['suggestions'])}")
        console.print()


if __name__ == "__main__":
    console.print("[bold green]Snowflake AI Agent - Example Usage[/bold green]\n")
    
    try:
        example_basic_usage()
        example_with_execution()
        example_conversation_flow()
        example_session_management()
        example_error_handling()
        example_programmatic_usage()
        
        console.print("\n[bold green]All examples completed![/bold green]")
        
    except Exception as e:
        console.print(f"\n[red]Example execution failed: {e}[/red]")
        import traceback
        console.print(traceback.format_exc())