# Contributing

Thank you for considering contributing to the Rodrunner project! This guide will help you get started with contributing to the project.

## Development Environment

### Setting Up the Development Environment

1. Clone the repository:

```bash
git clone https://github.com/bilgehannevruz/rodrunner.git
cd rodrunner
```

2. Create a virtual environment and install dependencies:

Using `uv` (recommended):

```bash
uv venv .venv
source .venv/bin/activate
uv pip install -e ".[dev]"
```

Using `pip`:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

3. Set up pre-commit hooks:

```bash
pre-commit install
```

### Using Docker for Development

You can also use Docker for development:

```bash
docker-compose up -d
docker-compose exec app bash
```

## Code Style

The project follows the following code style guidelines:

- **Black**: For code formatting
- **isort**: For import sorting
- **mypy**: For type checking
- **flake8**: For linting

You can run the code style checks with:

```bash
# Format code
black .

# Sort imports
isort .

# Type check
mypy .

# Lint
flake8 .

# Run all checks
pre-commit run --all-files
```

## Testing

The project uses pytest for testing. You can run the tests with:

```bash
# Run all tests
pytest

# Run tests with coverage
pytest --cov=rodrunner

# Run specific tests
pytest tests/test_filesystem
```

For more information on testing, see the [Testing Guide](testing.md).

## Documentation

The project uses MkDocs for documentation. You can build and serve the documentation with:

```bash
# Install MkDocs and dependencies
pip install mkdocs mkdocs-material mkdocstrings

# Build the documentation
mkdocs build

# Serve the documentation
mkdocs serve
```

## Pull Request Process

1. Fork the repository
2. Create a new branch for your feature or bug fix
3. Make your changes
4. Run the tests and code style checks
5. Update the documentation if necessary
6. Submit a pull request

### Pull Request Guidelines

- Keep pull requests focused on a single feature or bug fix
- Write clear commit messages
- Include tests for new features or bug fixes
- Update the documentation if necessary
- Make sure all tests pass
- Make sure the code style checks pass

## Issue Reporting

If you find a bug or have a feature request, please create an issue on the GitHub repository.

### Bug Reports

When reporting a bug, please include:

- A clear and descriptive title
- A description of the expected behavior
- A description of the actual behavior
- Steps to reproduce the bug
- Any relevant logs or error messages
- Your environment (OS, Python version, etc.)

### Feature Requests

When requesting a feature, please include:

- A clear and descriptive title
- A description of the feature
- Why the feature would be useful
- Any relevant examples or use cases

## Code of Conduct

Please be respectful and considerate of others when contributing to the project. We strive to create a welcoming and inclusive environment for all contributors.

## License

By contributing to the project, you agree that your contributions will be licensed under the project's MIT License.

## Contact

If you have any questions or need help with contributing, please contact the project maintainers.
