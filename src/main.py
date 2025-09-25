"""Main entry point for the Snowflake AI Agent CLI application."""

import sys
import click
from typing import Optional
from loguru import logger
from rich.console import Console
from rich.prompt import Prompt
from rich.panel import Panel

from .agent import agent
from .snowflake_client import snowflake_client
from config.settings import app_settings


# Configure logging
logger.remove()
logger.add(
    sys.stderr,
    level=app_settings.log_level,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"
)

console = Console()


@click.group()
def cli():
    """Snowflake AI Agent - Natural language interface for Snowflake data warehouse."""
    pass


@cli.command()
@click.option('--session-id', help='Session ID to use or create')
def interactive(session_id: Optional[str]):
    """Start interactive mode for chatting with the AI agent."""
    console.print(Panel(
        "[bold blue]Snowflake AI Agent[/bold blue]\n"
        "Natural language interface for your Snowflake data warehouse.\n\n"
        "Commands:\n"
        "  • Type your questions in natural language\n"
        "  • Type 'help' for more options\n"
        "  • Type 'exit' or 'quit' to end session\n"
        "  • Type 'test' to test connection\n"
        "  • Type 'tables' to list available tables\n"
        "  • Type 'export <filename>' to export last results",
        title="Welcome",
        border_style="blue"
    ))
    
    # Test connection first
    console.print("Testing Snowflake connection...")
    try:
        if not snowflake_client.test_connection():
            console.print("[red]❌ Connection test failed. Please check your credentials.[/red]")
            return
        console.print("[green]✅ Connection successful![/green]")
    except Exception as e:
        console.print(f"[red]❌ Connection failed: {e}[/red]")
        return
    
    # Start agent session
    session_id = agent.start_session(session_id)
    console.print(f"[green]Started session: {session_id}[/green]")
    
    last_response = None
    
    while True:
        try:
            # Get user input
            user_input = Prompt.ask("\n[bold cyan]Ask me anything about your data")
            
            if not user_input:
                continue
            
            # Handle special commands
            if user_input.lower() in ['exit', 'quit', 'q']:
                break
            elif user_input.lower() == 'help':
                show_help()
                continue
            elif user_input.lower() == 'test':
                test_connection()
                continue
            elif user_input.lower() == 'tables':
                list_tables()
                continue
            elif user_input.lower().startswith('export '):
                filename = user_input[7:].strip()
                if last_response and filename:
                    agent.export_results_to_csv(last_response, filename)
                else:
                    console.print("[red]No results to export or filename not provided[/red]")
                continue
            elif user_input.lower() == 'session':
                show_session_info()
                continue
            
            # Process the query
            console.print("[yellow]🤔 Thinking...[/yellow]")
            response = agent.process_query(user_input)
            last_response = response
            
            # Display results
            agent.display_results(response)
            
        except KeyboardInterrupt:
            console.print("\n[yellow]Session interrupted by user[/yellow]")
            break
        except Exception as e:
            console.print(f"[red]Error: {e}[/red]")
            logger.error(f"Unexpected error in interactive mode: {e}")
    
    # Session summary
    summary = agent.get_session_summary()
    console.print(Panel(
        f"Session ID: {summary.get('session_id', 'Unknown')}\n"
        f"Queries processed: {summary.get('queries_executed', 0)}\n"
        f"Total messages: {summary.get('message_count', 0)}",
        title="[bold green]Session Summary",
        border_style="green"
    ))
    
    console.print("[bold blue]Thank you for using Snowflake AI Agent![/bold blue]")


@cli.command()
@click.argument('query')
@click.option('--execute/--no-execute', default=True, help='Execute the generated SQL query')
@click.option('--export', help='Export results to CSV file')
def query(query: str, execute: bool, export: Optional[str]):
    """Process a single natural language query."""
    # Test connection
    if not snowflake_client.test_connection():
        console.print("[red]❌ Connection test failed.[/red]")
        return
    
    # Start session and process query
    agent.start_session()
    response = agent.process_query(query, execute=execute)
    
    # Display results
    agent.display_results(response)
    
    # Export if requested
    if export and response.get("results"):
        agent.export_results_to_csv(response, export)


@cli.command()
def test():
    """Test the Snowflake connection."""
    test_connection()


@cli.command()
def tables():
    """List all available tables."""
    list_tables()


def show_help():
    """Show help information."""
    console.print(Panel(
        "[bold]Available Commands:[/bold]\n\n"
        "• [cyan]help[/cyan] - Show this help\n"
        "• [cyan]test[/cyan] - Test Snowflake connection\n"
        "• [cyan]tables[/cyan] - List available tables\n"
        "• [cyan]session[/cyan] - Show session information\n"
        "• [cyan]export <filename>[/cyan] - Export last results to CSV\n"
        "• [cyan]exit/quit[/cyan] - End session\n\n"
        "[bold]Example queries:[/bold]\n"
        "• 'Show me the top 10 customers by revenue'\n"
        "• 'What are the sales numbers for last month?'\n"
        "• 'Count orders by region'\n"
        "• 'Show me product categories and their average prices'",
        title="Help",
        border_style="cyan"
    ))


def test_connection():
    """Test Snowflake connection."""
    console.print("Testing Snowflake connection...")
    try:
        if snowflake_client.test_connection():
            console.print("[green]✅ Connection successful![/green]")
        else:
            console.print("[red]❌ Connection failed.[/red]")
    except Exception as e:
        console.print(f"[red]❌ Connection failed: {e}[/red]")


def list_tables():
    """List available tables."""
    try:
        console.print("Fetching table list...")
        tables = snowflake_client.list_tables()
        
        if tables:
            console.print(f"[green]Found {len(tables)} tables:[/green]")
            for table in tables:
                console.print(f"  • {table}")
        else:
            console.print("[yellow]No tables found.[/yellow]")
            
    except Exception as e:
        console.print(f"[red]Failed to list tables: {e}[/red]")


def show_session_info():
    """Show current session information."""
    summary = agent.get_session_summary()
    if "error" in summary:
        console.print("[yellow]No active session[/yellow]")
    else:
        console.print(Panel(
            f"Session ID: {summary['session_id']}\n"
            f"Created: {summary['created_at']}\n"
            f"Messages: {summary['message_count']}\n"
            f"Queries: {summary['queries_executed']}",
            title="Session Info",
            border_style="blue"
        ))


if __name__ == "__main__":
    cli()