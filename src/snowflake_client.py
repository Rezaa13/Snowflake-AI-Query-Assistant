"""Snowflake database client for executing queries and managing connections."""

import snowflake.connector
from snowflake.connector import DictCursor
import pandas as pd
from typing import List, Dict, Any, Optional
from loguru import logger
import contextlib
import os
import getpass

from config.settings import snowflake_settings, app_settings


class SnowflakeClient:
    """Client for managing Snowflake database connections and query execution."""
    
    def __init__(self):
        """Initialize the Snowflake client."""
        self.connection = None
        self._connection_params = {
            'account': snowflake_settings.account,
            'user': snowflake_settings.user,
            'warehouse': snowflake_settings.warehouse,
            'database': snowflake_settings.database,
            'schema': snowflake_settings.schema,
        }
        
        if snowflake_settings.role:
            self._connection_params['role'] = snowflake_settings.role
        
        # Handle authentication based on available methods
        self._setup_authentication()
    
    def _setup_authentication(self):
        """Set up authentication method based on available credentials."""
        # Method 1: Private Key Authentication (most secure)
        private_key_path = getattr(snowflake_settings, 'private_key_path', None)
        private_key_passphrase = getattr(snowflake_settings, 'private_key_passphrase', None)
        
        if private_key_path and os.path.exists(private_key_path):
            logger.info("Using private key authentication")
            self._setup_private_key_auth(private_key_path, private_key_passphrase)
            return
        
        # Method 2: SSO/OAuth (if available)
        authenticator = getattr(snowflake_settings, 'authenticator', None)
        if authenticator:
            logger.info(f"Using authenticator: {authenticator}")
            self._connection_params['authenticator'] = authenticator
            
            # For externalbrowser SSO
            if authenticator.lower() == 'externalbrowser':
                return
            
            # For OAuth
            if authenticator.lower() == 'oauth':
                oauth_token = getattr(snowflake_settings, 'oauth_token', None)
                if oauth_token:
                    self._connection_params['token'] = oauth_token
                return
        
        # Method 3: Environment variable password (better than hardcoded)
        password_from_env = os.getenv('SNOWFLAKE_PASSWORD_SECURE')
        if password_from_env:
            logger.info("Using password from secure environment variable")
            self._connection_params['password'] = password_from_env
            return
        
        # Method 4: Interactive password prompt (most secure for development)
        if hasattr(snowflake_settings, 'password') and snowflake_settings.password:
            if snowflake_settings.password == 'your_password' or snowflake_settings.password == 'PROMPT':
                logger.info("Password not configured, will prompt for password")
                self._connection_params['password'] = None  # Will prompt later
            else:
                self._connection_params['password'] = snowflake_settings.password
        else:
            logger.info("No password configured, will prompt for password")
            self._connection_params['password'] = None
    
    def _setup_private_key_auth(self, private_key_path: str, passphrase: Optional[str] = None):
        """Set up private key authentication."""
        try:
            from cryptography.hazmat.primitives import serialization
            from cryptography.hazmat.primitives.serialization import pkcs8
            
            with open(private_key_path, 'rb') as key_file:
                if passphrase:
                    passphrase_bytes = passphrase.encode('utf-8')
                else:
                    passphrase_bytes = None
                    
                private_key = serialization.load_pem_private_key(
                    key_file.read(),
                    password=passphrase_bytes
                )
            
            private_key_bytes = private_key.private_bytes(
                encoding=serialization.Encoding.DER,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption()
            )
            
            self._connection_params['private_key'] = private_key_bytes
            # Remove password if using private key
            self._connection_params.pop('password', None)
            
        except ImportError:
            logger.error("cryptography package required for private key authentication")
            logger.error("Install with: pip install cryptography")
            raise
        except Exception as e:
            logger.error(f"Failed to load private key: {e}")
            raise
    
    def connect(self) -> None:
        """Establish connection to Snowflake."""
        try:
            # Handle interactive password prompt if needed
            if self._connection_params.get('password') is None and 'private_key' not in self._connection_params:
                if self._connection_params.get('authenticator') != 'externalbrowser':
                    print(f"Please enter password for Snowflake user '{self._connection_params['user']}':")
                    password = getpass.getpass()
                    self._connection_params['password'] = password
            
            self.connection = snowflake.connector.connect(**self._connection_params)
            logger.info("Successfully connected to Snowflake")
        except Exception as e:
            logger.error(f"Failed to connect to Snowflake: {e}")
            raise
    
    def disconnect(self) -> None:
        """Close the Snowflake connection."""
        if self.connection:
            self.connection.close()
            self.connection = None
            logger.info("Disconnected from Snowflake")
    
    @contextlib.contextmanager
    def get_cursor(self):
        """Context manager for getting a database cursor."""
        if not self.connection:
            self.connect()
        
        cursor = self.connection.cursor(DictCursor)
        try:
            yield cursor
        finally:
            cursor.close()
    
    def execute_query(self, query: str, fetch_results: bool = True) -> Optional[List[Dict[str, Any]]]:
        """
        Execute a SQL query and return results.
        
        Args:
            query: SQL query to execute
            fetch_results: Whether to fetch and return results
            
        Returns:
            List of dictionaries containing query results, or None if fetch_results is False
        """
        try:
            with self.get_cursor() as cursor:
                logger.info(f"Executing query: {query[:100]}...")
                
                cursor.execute(query)
                
                if fetch_results:
                    results = cursor.fetchall()
                    logger.info(f"Query returned {len(results)} rows")
                    return results
                else:
                    logger.info("Query executed successfully (no results fetched)")
                    return None
                    
        except Exception as e:
            logger.error(f"Query execution failed: {e}")
            raise
    
    def execute_query_to_dataframe(self, query: str) -> pd.DataFrame:
        """
        Execute a SQL query and return results as a pandas DataFrame.
        
        Args:
            query: SQL query to execute
            
        Returns:
            pandas DataFrame containing query results
        """
        try:
            with self.get_cursor() as cursor:
                logger.info(f"Executing query to DataFrame: {query[:100]}...")
                
                cursor.execute(query)
                df = cursor.fetch_pandas_all()
                
                logger.info(f"Query returned DataFrame with shape {df.shape}")
                return df
                
        except Exception as e:
            logger.error(f"Query to DataFrame failed: {e}")
            raise
    
    def get_table_info(self, table_name: str) -> List[Dict[str, Any]]:
        """
        Get information about a table's columns.
        
        Args:
            table_name: Name of the table
            
        Returns:
            List of dictionaries containing column information
        """
        query = f"""
        SELECT 
            COLUMN_NAME,
            DATA_TYPE,
            IS_NULLABLE,
            COLUMN_DEFAULT,
            COMMENT
        FROM INFORMATION_SCHEMA.COLUMNS 
        WHERE TABLE_NAME = UPPER('{table_name}')
        AND TABLE_SCHEMA = UPPER('{snowflake_settings.schema or "PUBLIC"}')
        AND TABLE_CATALOG = UPPER('{snowflake_settings.database or ""}')
        ORDER BY ORDINAL_POSITION
        """
        
        return self.execute_query(query)
    
    def list_tables(self) -> List[str]:
        """
        List all tables in the current schema.
        
        Returns:
            List of table names
        """
        query = f"""
        SELECT TABLE_NAME
        FROM INFORMATION_SCHEMA.TABLES
        WHERE TABLE_SCHEMA = UPPER('{snowflake_settings.schema or "PUBLIC"}')
        AND TABLE_CATALOG = UPPER('{snowflake_settings.database or ""}')
        AND TABLE_TYPE = 'BASE TABLE'
        ORDER BY TABLE_NAME
        """
        
        results = self.execute_query(query)
        return [row['TABLE_NAME'] for row in results] if results else []
    
    def get_sample_data(self, table_name: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Get sample data from a table.
        
        Args:
            table_name: Name of the table
            limit: Number of sample rows to return
            
        Returns:
            List of dictionaries containing sample data
        """
        query = f"SELECT * FROM {table_name} LIMIT {limit}"
        return self.execute_query(query)
    
    def test_connection(self) -> bool:
        """
        Test the Snowflake connection.
        
        Returns:
            True if connection is successful, False otherwise
        """
        try:
            self.connect()
            result = self.execute_query("SELECT CURRENT_VERSION()")
            logger.info(f"Connection test successful. Snowflake version: {result[0] if result else 'Unknown'}")
            return True
        except Exception as e:
            logger.error(f"Connection test failed: {e}")
            return False
        finally:
            self.disconnect()


# Global client instance
snowflake_client = SnowflakeClient()