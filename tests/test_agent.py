"""Test suite for the Snowflake AI Agent."""

import pytest
import sys
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

# Add src to path
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

from agent import SnowflakeAIAgent, ConversationMessage, AgentSession
from query_translator import QueryTranslator, QueryContext
from snowflake_client import SnowflakeClient
from conversation_manager import ConversationManager


class TestSnowflakeClient:
    """Test cases for SnowflakeClient."""
    
    def test_connection_params_setup(self):
        """Test that connection parameters are set up correctly."""
        client = SnowflakeClient()
        
        # Check that connection params are initialized
        assert hasattr(client, '_connection_params')
        assert 'account' in client._connection_params
        assert 'user' in client._connection_params
        assert 'password' in client._connection_params
    
    @patch('snowflake.connector.connect')
    def test_connect_success(self, mock_connect):
        """Test successful connection."""
        mock_connection = Mock()
        mock_connect.return_value = mock_connection
        
        client = SnowflakeClient()
        client.connect()
        
        assert client.connection == mock_connection
        mock_connect.assert_called_once()
    
    @patch('snowflake.connector.connect')
    def test_connect_failure(self, mock_connect):
        """Test connection failure handling."""
        mock_connect.side_effect = Exception("Connection failed")
        
        client = SnowflakeClient()
        
        with pytest.raises(Exception):
            client.connect()


class TestQueryTranslator:
    """Test cases for QueryTranslator."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.translator = QueryTranslator()
    
    def test_create_system_prompt(self):
        """Test system prompt creation."""
        context = QueryContext(
            table_schemas={
                "customers": [
                    {"COLUMN_NAME": "id", "DATA_TYPE": "NUMBER", "COMMENT": "Customer ID"},
                    {"COLUMN_NAME": "name", "DATA_TYPE": "VARCHAR", "COMMENT": "Customer name"}
                ]
            },
            sample_data={
                "customers": [{"id": 1, "name": "John Doe"}]
            },
            conversation_history=[]
        )
        
        prompt = self.translator.create_system_prompt(context)
        
        assert "customers" in prompt
        assert "COLUMN_NAME" in prompt
        assert "DATA_TYPE" in prompt
        assert "sample" in prompt.lower()
    
    def test_validate_query_valid(self):
        """Test query validation for valid queries."""
        valid_queries = [
            "SELECT * FROM customers",
            "SELECT COUNT(*) FROM orders WHERE date > '2023-01-01'",
            "WITH cte AS (SELECT id FROM customers) SELECT * FROM cte"
        ]
        
        for query in valid_queries:
            result = self.translator.validate_query(query)
            assert result["is_valid"] == True
    
    def test_validate_query_warnings(self):
        """Test query validation warnings."""
        dangerous_query = "DROP TABLE customers"
        result = self.translator.validate_query(dangerous_query)
        
        assert len(result["warnings"]) > 0
        assert any("dangerous" in warning.lower() for warning in result["warnings"])
    
    def test_suggest_improvements(self):
        """Test query improvement suggestions."""
        query_without_limit = "SELECT * FROM large_table"
        suggestions = self.translator.suggest_improvements(query_without_limit)
        
        assert len(suggestions) > 0
        assert any("LIMIT" in suggestion for suggestion in suggestions)


class TestSnowflakeAIAgent:
    """Test cases for SnowflakeAIAgent."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.agent = SnowflakeAIAgent()
    
    def test_start_session(self):
        """Test session creation."""
        session_id = self.agent.start_session("test_session")
        
        assert session_id == "test_session"
        assert self.agent.current_session is not None
        assert self.agent.current_session.session_id == "test_session"
    
    def test_start_session_auto_id(self):
        """Test session creation with auto-generated ID."""
        session_id = self.agent.start_session()
        
        assert session_id.startswith("session_")
        assert self.agent.current_session is not None
    
    @patch('src.snowflake_client.snowflake_client.list_tables')
    @patch('src.snowflake_client.snowflake_client.get_table_info')
    @patch('src.snowflake_client.snowflake_client.get_sample_data')
    def test_load_database_context(self, mock_sample, mock_info, mock_tables):
        """Test database context loading."""
        # Mock data
        mock_tables.return_value = ["customers", "orders"]
        mock_info.return_value = [
            {"COLUMN_NAME": "id", "DATA_TYPE": "NUMBER", "COMMENT": "ID"}
        ]
        mock_sample.return_value = [{"id": 1}]
        
        context = self.agent.load_database_context(use_cache=False)
        
        assert "customers" in context.table_schemas
        assert "orders" in context.table_schemas
        assert len(context.table_schemas["customers"]) > 0
    
    def test_get_session_summary_no_session(self):
        """Test session summary when no session exists."""
        summary = self.agent.get_session_summary()
        
        assert "error" in summary
    
    def test_get_session_summary_with_session(self):
        """Test session summary with active session."""
        self.agent.start_session("test")
        summary = self.agent.get_session_summary()
        
        assert "session_id" in summary
        assert summary["session_id"] == "test"
        assert "message_count" in summary


class TestConversationManager:
    """Test cases for ConversationManager."""
    
    def setup_method(self):
        """Set up test fixtures."""
        import tempfile
        self.temp_dir = tempfile.mkdtemp()
        self.manager = ConversationManager(self.temp_dir)
    
    def teardown_method(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_save_and_load_session(self):
        """Test saving and loading sessions."""
        # Create test session
        session = AgentSession(
            session_id="test_session",
            created_at=datetime.now()
        )
        
        # Add a test message
        message = ConversationMessage(
            timestamp=datetime.now(),
            role="user",
            content="Test message"
        )
        session.messages.append(message)
        
        # Save session
        saved_path = self.manager.save_session(session)
        assert saved_path is not None
        
        # Load session
        loaded_session = self.manager.load_session("test_session")
        assert loaded_session is not None
        assert loaded_session.session_id == "test_session"
        assert len(loaded_session.messages) == 1
        assert loaded_session.messages[0].content == "Test message"
    
    def test_list_sessions(self):
        """Test listing sessions."""
        # Create and save test sessions
        for i in range(3):
            session = AgentSession(
                session_id=f"test_session_{i}",
                created_at=datetime.now()
            )
            self.manager.save_session(session)
        
        # List sessions
        sessions = self.manager.list_sessions()
        assert len(sessions) == 3
        assert all("session_id" in s for s in sessions)
    
    def test_delete_session(self):
        """Test deleting sessions."""
        # Create and save test session
        session = AgentSession(
            session_id="test_delete",
            created_at=datetime.now()
        )
        self.manager.save_session(session)
        
        # Verify it exists
        loaded = self.manager.load_session("test_delete")
        assert loaded is not None
        
        # Delete it
        deleted = self.manager.delete_session("test_delete")
        assert deleted == True
        
        # Verify it's gone
        loaded = self.manager.load_session("test_delete")
        assert loaded is None


@pytest.fixture
def mock_openai():
    """Mock OpenAI API responses."""
    with patch('openai.chat.completions.create') as mock:
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "SELECT * FROM customers LIMIT 10"
        mock.return_value = mock_response
        yield mock


class TestIntegration:
    """Integration test cases."""
    
    @patch('src.snowflake_client.snowflake_client.test_connection')
    @patch('src.snowflake_client.snowflake_client.list_tables')
    @patch('src.snowflake_client.snowflake_client.get_table_info')
    @patch('src.snowflake_client.snowflake_client.get_sample_data')
    def test_end_to_end_query_processing(self, mock_sample, mock_info, 
                                       mock_tables, mock_test, mock_openai):
        """Test end-to-end query processing."""
        # Mock Snowflake responses
        mock_test.return_value = True
        mock_tables.return_value = ["customers"]
        mock_info.return_value = [
            {"COLUMN_NAME": "id", "DATA_TYPE": "NUMBER", "COMMENT": "ID"}
        ]
        mock_sample.return_value = [{"id": 1}]
        
        # Create agent and process query
        agent = SnowflakeAIAgent()
        response = agent.process_query("Show me all customers", execute=False)
        
        # Verify response structure
        assert "natural_language" in response
        assert "sql_query" in response
        assert "validation" in response
        assert response["natural_language"] == "Show me all customers"


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])