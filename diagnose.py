"""Diagnostic script to help troubleshoot Snowflake connection issues."""

import sys
import os
sys.path.insert(0, 'src')

from config.settings import snowflake_settings
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

console = Console()

def diagnose_connection():
    """Diagnose Snowflake connection configuration."""
    
    console.print(Panel(
        "[bold blue]Snowflake Connection Diagnostics[/bold blue]",
        title="🔍 Diagnostics",
        border_style="blue"
    ))
    
    # Show current configuration
    table = Table(title="Current Configuration")
    table.add_column("Parameter", style="cyan")
    table.add_column("Value", style="white")
    table.add_column("Status", style="green")
    
    # Check account
    account = snowflake_settings.account
    table.add_row("Account", account, "✅ Set" if account else "❌ Missing")
    
    # Check user
    user = snowflake_settings.user
    table.add_row("User", user, "✅ Set" if user else "❌ Missing")
    
    # Check authenticator
    auth = snowflake_settings.authenticator
    table.add_row("Authenticator", auth or "password", "✅ Set" if auth else "🔑 Password")
    
    # Check role
    role = snowflake_settings.role
    table.add_row("Role", role or "Default", "✅ Set" if role else "ℹ️ Default")
    
    # Check warehouse
    warehouse = snowflake_settings.warehouse
    table.add_row("Warehouse", warehouse or "Not specified", "⚠️ Empty" if not warehouse else "✅ Set")
    
    # Check database
    database = snowflake_settings.database
    table.add_row("Database", database or "Not specified", "⚠️ Empty" if not database else "✅ Set")
    
    # Check schema
    schema = snowflake_settings.snowflake_schema
    table.add_row("Schema", schema or "Not specified", "⚠️ Empty" if not schema else "✅ Set")
    
    console.print(table)
    
    # Suggestions
    console.print("\n[bold cyan]💡 Troubleshooting Suggestions:[/bold cyan]")
    
    suggestions = []
    
    if not warehouse:
        suggestions.append("Set SNOWFLAKE_WAREHOUSE (e.g., COMPUTE_WH)")
    
    if not database:
        suggestions.append("Set SNOWFLAKE_DATABASE to a database you have access to")
    
    if auth == "externalbrowser":
        suggestions.append("For SSO: Ensure your Snowflake account is configured for SSO/SAML")
        suggestions.append("For SSO: Try logging in through Snowflake web UI first")
        suggestions.append("For SSO: Contact your Snowflake admin about SSO configuration")
    
    if not auth:
        suggestions.append("For password auth: Ensure username and password are correct")
        suggestions.append("For password auth: Check if account requires MFA")
    
    suggestions.append("Try connecting with Snowflake's official CLI: snow connection test")
    suggestions.append("Verify account name format: should be ACCOUNT-ID (without .snowflakecomputing.com)")
    
    for i, suggestion in enumerate(suggestions, 1):
        console.print(f"  {i}. {suggestion}")
    
    # Test connection URL format
    console.print(f"\n[bold yellow]🌐 Connection URL would be:[/bold yellow]")
    console.print(f"   https://{account}.snowflakecomputing.com")
    
    console.print("\n[bold green]🚀 Next Steps:[/bold green]")
    console.print("1. Update your .env file with correct parameters")
    console.print("2. Try: python -m src.main test")
    console.print("3. If still failing, check with your Snowflake administrator")
    
    # Show .env file location
    env_path = os.path.join(os.getcwd(), '.env')
    console.print(f"\n[dim]📁 Your .env file location: {env_path}[/dim]")

if __name__ == "__main__":
    try:
        diagnose_connection()
    except Exception as e:
        console.print(f"[red]Error running diagnostics: {e}[/red]")
        console.print("\nPlease check your .env file configuration.")