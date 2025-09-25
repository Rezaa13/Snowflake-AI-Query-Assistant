# Contributing to Snowflake AI Agent

Thank you for your interest in contributing to the Snowflake AI Agent project! This guide will help you get started.

## Development Setup

1. **Clone the repository:**
   ```bash
   git clone <repository_url>
   cd snowflake
   ```

2. **Set up virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   pip install -e .  # Install in development mode
   ```

4. **Set up environment variables:**
   ```bash
   cp .env.example .env
   # Edit .env with your credentials
   ```

## Project Structure

```
snowflake/
├── src/                    # Main source code
│   ├── __init__.py
│   ├── main.py            # CLI entry point
│   ├── agent.py           # Main AI agent class
│   ├── snowflake_client.py # Snowflake connectivity
│   ├── query_translator.py # Natural language to SQL
│   └── conversation_manager.py # Session management
├── config/                # Configuration files
│   └── settings.py        # Application settings
├── tests/                 # Test suite
│   └── test_agent.py      # Main test file
├── examples/              # Usage examples
│   └── example_usage.py   # Example scripts
├── requirements.txt       # Python dependencies
├── .env.example          # Environment template
└── README.md             # Project documentation
```

## Code Style and Standards

### Python Style
- Follow PEP 8 style guidelines
- Use type hints for function parameters and return values
- Document all public functions and classes with docstrings
- Maximum line length: 88 characters (Black formatter default)

### Code Formatting
We use automated code formatting tools:

```bash
# Format code
black src/ tests/ examples/

# Check style
flake8 src/ tests/ examples/

# Type checking
mypy src/
```

### Commit Messages
Use conventional commit format:
- `feat:` for new features
- `fix:` for bug fixes
- `docs:` for documentation changes
- `test:` for test additions/changes
- `refactor:` for code refactoring

Example: `feat: add support for complex JOIN queries`

## Testing

### Running Tests
```bash
# Run all tests
pytest tests/

# Run with coverage
pytest tests/ --cov=src --cov-report=html

# Run specific test file
pytest tests/test_agent.py -v
```

### Writing Tests
- Write unit tests for all new functionality
- Use pytest fixtures for common test setup
- Mock external dependencies (Snowflake, OpenAI API)
- Aim for >80% code coverage

### Test Categories
1. **Unit Tests**: Test individual components
2. **Integration Tests**: Test component interactions
3. **End-to-End Tests**: Test complete workflows

## Adding New Features

### 1. Planning
- Create an issue describing the feature
- Discuss implementation approach
- Consider backward compatibility

### 2. Implementation
- Create a feature branch: `git checkout -b feature/your-feature-name`
- Write code following established patterns
- Add comprehensive tests
- Update documentation

### 3. Validation
- Ensure all tests pass
- Test with real Snowflake instance if possible
- Check code coverage
- Update examples if needed

### 4. Submission
- Create a pull request with clear description
- Link to related issues
- Ensure CI checks pass
- Respond to review feedback

## Common Development Tasks

### Adding a New Query Type
1. Extend `QueryTranslator` with new patterns
2. Update system prompt in `create_system_prompt()`
3. Add validation rules in `validate_query()`
4. Add tests and examples

### Adding New Snowflake Features
1. Extend `SnowflakeClient` with new methods
2. Update connection parameters if needed
3. Add error handling and logging
4. Test with different Snowflake configurations

### Improving AI Responses
1. Update prompt templates in `QueryTranslator`
2. Add context handling in `load_database_context()`
3. Improve conversation history management
4. Test with various query types

## Documentation

### Code Documentation
- Use Google-style docstrings
- Include parameter types and descriptions
- Provide usage examples for complex functions
- Document any non-obvious logic

### User Documentation
- Update README.md for user-facing changes
- Add examples for new features
- Update configuration documentation
- Keep troubleshooting guide current

## Performance Considerations

### Database Queries
- Use LIMIT clauses to prevent large result sets
- Cache schema information when possible
- Implement query timeouts
- Log performance metrics

### AI API Calls
- Optimize prompt length to reduce token usage
- Implement retry logic for API failures
- Cache common query translations
- Monitor API usage and costs

### Memory Usage
- Stream large result sets when possible
- Clean up old conversation sessions
- Implement result pagination for large datasets

## Security Guidelines

### Credentials Management
- Never commit credentials to version control
- Use environment variables for sensitive data
- Implement secure credential storage
- Support multiple authentication methods

### Query Safety
- Validate all generated SQL queries
- Prevent dangerous operations (DROP, DELETE)
- Implement query whitelisting if needed
- Log all executed queries for audit

### Data Privacy
- Don't log sensitive query results
- Implement data masking for examples
- Follow data retention policies
- Respect user privacy settings

## Release Process

### Version Numbering
We follow semantic versioning (SemVer):
- MAJOR: Breaking changes
- MINOR: New features (backward compatible)
- PATCH: Bug fixes (backward compatible)

### Release Checklist
1. Update version numbers
2. Update CHANGELOG.md
3. Run full test suite
4. Update documentation
5. Create release tag
6. Deploy to package registry

## Getting Help

### Development Questions
- Check existing issues and discussions
- Create a new issue with [question] tag
- Join our development chat (if available)

### Bug Reports
When reporting bugs, include:
- Python version and OS
- Snowflake version and configuration
- Complete error messages and stack traces
- Minimal reproduction example
- Expected vs actual behavior

### Feature Requests
When requesting features:
- Describe the use case clearly
- Provide examples of desired behavior
- Consider implementation complexity
- Discuss alternatives if applicable

## Code Review Guidelines

### For Authors
- Keep changes focused and atomic
- Write clear commit messages
- Add tests for new functionality
- Update documentation as needed
- Respond promptly to review feedback

### For Reviewers
- Focus on code correctness and style
- Check for potential security issues
- Verify test coverage
- Suggest improvements constructively
- Approve when ready for merge

Thank you for contributing to the Snowflake AI Agent project! Your contributions help make data analysis more accessible to everyone.