# Contributing to Agentic AI Investment Research Assistant

Thank you for your interest in contributing! This document provides guidelines for contributing to this project.

## Table of Contents

1. [Code of Conduct](#code-of-conduct)
2. [Getting Started](#getting-started)
3. [Development Setup](#development-setup)
4. [Making Changes](#making-changes)
5. [Testing](#testing)
6. [Documentation](#documentation)
7. [Submitting Changes](#submitting-changes)

## Code of Conduct

### Our Standards

- Be respectful and inclusive
- Welcome newcomers and help them learn
- Focus on constructive feedback
- Respect different viewpoints and experiences
- Accept responsibility for mistakes

## Getting Started

### Prerequisites

- Python 3.9 or higher
- Git for version control
- Virtual environment tool (venv, conda)
- Basic understanding of AI agents and LLMs

### Areas for Contribution

1. **New Tools**: Add tools for additional financial analytics
2. **Improved Planning**: Enhance agent planning strategies
3. **RAG System**: Implement document retrieval
4. **Testing**: Add unit and integration tests
5. **Documentation**: Improve guides and examples
6. **Bug Fixes**: Fix reported issues
7. **Performance**: Optimize execution speed

## Development Setup

### 1. Fork and Clone

```bash
# Fork the repository on GitHub first

# Clone your fork
git clone https://github.com/YOUR_USERNAME/project1.git
cd project1

# Add upstream remote
git remote add upstream https://github.com/sanathpabba/project1.git
```

### 2. Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
# Install main dependencies
pip install -r requirements.txt

# Install development dependencies
pip install pytest pytest-cov black flake8 mypy pylint
```

### 4. Configure Environment

```bash
cp .env.example .env
# Edit .env with your test API keys
```

### 5. Verify Setup

```bash
# Run tests
pytest tests/

# Run linter
flake8 src/

# Check types
mypy src/
```

## Making Changes

### Branch Naming

Use descriptive branch names:

```bash
# Features
git checkout -b feature/add-momentum-tool

# Bug fixes
git checkout -b fix/sharpe-ratio-calculation

# Documentation
git checkout -b docs/improve-quickstart

# Refactoring
git checkout -b refactor/tool-registry
```

### Code Style

#### Python Style Guide

Follow PEP 8 with these guidelines:

```python
# Good: Clear function names, type hints, docstrings
def calculate_sharpe_ratio(
    returns: List[float],
    risk_free_rate: float = 0.02
) -> float:
    """
    Calculate Sharpe ratio from returns.
    
    Args:
        returns: List of periodic returns
        risk_free_rate: Risk-free rate (default: 0.02)
    
    Returns:
        Calculated Sharpe ratio
    """
    # Implementation
    pass

# Bad: No types, no docstring, unclear naming
def calc(r, rf=0.02):
    pass
```

#### Key Conventions

1. **Type Hints**: Always use type hints for function signatures
2. **Docstrings**: All public functions, classes, modules need docstrings
3. **Naming**: Use descriptive names, follow PEP 8
4. **Line Length**: Max 100 characters (slightly more permissive than PEP 8's 79)
5. **Imports**: Group into stdlib, third-party, local (separated by blank lines)

### Code Quality

#### Before Committing

```bash
# Format code
black src/ tests/

# Check style
flake8 src/ tests/

# Check types
mypy src/

# Run tests
pytest tests/
```

#### Automated Checks

The project uses pre-commit hooks (optional):

```bash
pip install pre-commit
pre-commit install
```

## Testing

### Writing Tests

Create tests in `tests/` directory:

```python
# tests/test_tools/test_financial_calc.py
import pytest
from src.tools.financial_calc import CalculateSharpeRatioTool

def test_sharpe_ratio_calculation():
    """Test Sharpe ratio calculation with known values."""
    tool = CalculateSharpeRatioTool()
    
    returns = [0.01, 0.02, -0.01, 0.03, 0.01]
    result = tool.execute({
        "returns": returns,
        "risk_free_rate": 0.02
    })
    
    assert isinstance(result, float)
    assert -5.0 <= result <= 5.0  # Reasonable range

def test_sharpe_ratio_empty_returns():
    """Test Sharpe ratio with empty returns."""
    tool = CalculateSharpeRatioTool()
    
    result = tool.execute({"returns": []})
    
    assert result == 0.0
```

### Running Tests

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_tools/test_financial_calc.py

# Run with coverage
pytest --cov=src tests/

# Run with verbose output
pytest -v

# Run specific test
pytest tests/test_tools/test_financial_calc.py::test_sharpe_ratio_calculation
```

### Test Guidelines

1. **Coverage**: Aim for >80% code coverage
2. **Unit Tests**: Test individual functions/classes
3. **Integration Tests**: Test component interactions
4. **Mock External Calls**: Mock LLM and API calls
5. **Test Data**: Use fixtures for reusable test data

## Documentation

### Docstring Format

Use Google-style docstrings:

```python
def execute_tool(
    tool_name: str,
    input_params: Dict[str, Any],
    state: Optional[Dict[str, Any]] = None
) -> Any:
    """
    Execute a tool with given parameters.
    
    This method handles tool execution with automatic retries
    and error logging.
    
    Args:
        tool_name: Name of the tool to execute
        input_params: Dictionary of input parameters
        state: Optional execution state
    
    Returns:
        Result from tool execution
    
    Raises:
        ValueError: If tool is not found
        ToolExecutionError: If tool execution fails
    
    Example:
        >>> executor = ToolExecutor(tools)
        >>> result = executor.execute_tool(
        ...     "portfolio_summary",
        ...     {},
        ...     state
        ... )
    """
    pass
```

### Documentation Files

When adding features, update:

1. **README.md**: If adding major features
2. **ARCHITECTURE.md**: If changing system design
3. **API.md**: If adding new public APIs
4. **Examples**: Add usage examples
5. **Inline Comments**: For complex logic

## Submitting Changes

### Commit Messages

Follow conventional commits format:

```bash
# Format: <type>(<scope>): <subject>

# Types: feat, fix, docs, style, refactor, test, chore

# Good examples
git commit -m "feat(tools): add momentum indicator tool"
git commit -m "fix(planner): handle empty plan response"
git commit -m "docs(readme): update installation instructions"
git commit -m "test(agent): add orchestrator integration tests"

# Bad examples
git commit -m "updates"
git commit -m "fixed stuff"
```

### Pull Request Process

#### 1. Update Your Fork

```bash
git fetch upstream
git checkout main
git merge upstream/main
```

#### 2. Create Feature Branch

```bash
git checkout -b feature/your-feature-name
```

#### 3. Make Changes

- Write code following style guidelines
- Add tests for new functionality
- Update documentation
- Ensure all tests pass

#### 4. Commit Changes

```bash
git add .
git commit -m "feat(scope): descriptive message"
```

#### 5. Push to Fork

```bash
git push origin feature/your-feature-name
```

#### 6. Create Pull Request

On GitHub:

1. Go to your fork
2. Click "New Pull Request"
3. Select your feature branch
4. Fill out PR template

#### PR Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] Unit tests pass
- [ ] Integration tests pass
- [ ] Manual testing completed

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Comments added for complex code
- [ ] Documentation updated
- [ ] No new warnings generated
- [ ] Tests added for new features
- [ ] All tests passing
```

### Review Process

1. **Automated Checks**: CI runs tests and linters
2. **Code Review**: Maintainer reviews code
3. **Feedback**: Address review comments
4. **Approval**: Once approved, PR is merged

### After Merge

```bash
# Update your local main
git checkout main
git pull upstream main

# Delete feature branch
git branch -d feature/your-feature-name
git push origin --delete feature/your-feature-name
```

## Adding New Tools

### Tool Implementation Template

```python
# src/tools/my_new_tool.py
from typing import Dict, Any, Optional
from .base import BaseTool, ToolMetadata, ToolCategory

class MyNewTool(BaseTool):
    """Tool for [purpose]."""
    
    def __init__(self):
        metadata = ToolMetadata(
            name="my_new_tool",
            description="Clear description of what this tool does",
            category=ToolCategory.ANALYTICS,  # Choose appropriate category
            parameters={
                "required_param": {
                    "type": "string",
                    "description": "What this parameter does",
                    "required": True
                },
                "optional_param": {
                    "type": "float",
                    "description": "Optional parameter",
                    "required": False,
                    "default": 0.0
                }
            },
            risk_level="low",  # low, medium, or high
            rate_limit=60  # calls per minute
        )
        super().__init__(metadata)
    
    def execute(
        self,
        input_params: Dict[str, Any],
        state: Optional[Dict[str, Any]] = None
    ) -> Any:
        """
        Execute the tool.
        
        Args:
            input_params: Tool parameters
            state: Execution state
        
        Returns:
            Tool result
        """
        self.validate_input(input_params)
        
        # Implementation
        result = self._do_work(input_params)
        
        return result
    
    def _do_work(self, params: Dict[str, Any]) -> Any:
        """Private helper method."""
        # Implementation
        pass
```

### Register New Tool

Add to `src/tools/registry.py`:

```python
def _initialize_tools(self):
    # ... existing tools ...
    
    from .my_new_tool import MyNewTool
    self.register(MyNewTool())
```

### Add Tests

Create `tests/test_tools/test_my_new_tool.py`:

```python
import pytest
from src.tools.my_new_tool import MyNewTool

def test_my_new_tool_basic():
    tool = MyNewTool()
    result = tool.execute({"required_param": "value"})
    assert result is not None

def test_my_new_tool_validation():
    tool = MyNewTool()
    with pytest.raises(ValueError):
        tool.execute({})  # Missing required parameter
```

## Getting Help

### Resources

- **Documentation**: Check `docs/` directory
- **Examples**: See `examples/` directory
- **Issues**: Search existing issues on GitHub
- **Discussions**: Use GitHub Discussions for questions

### Communication

- **Questions**: Open a GitHub Discussion
- **Bugs**: Open a GitHub Issue
- **Features**: Open a GitHub Issue with "enhancement" label
- **Security**: Email directly (see README for contact)

## Recognition

Contributors will be:
- Listed in CONTRIBUTORS.md
- Mentioned in release notes
- Credited in relevant documentation

Thank you for contributing! 🎉
