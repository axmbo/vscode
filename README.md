# Task Manager Web Application

A simple Flask-based task manager with SQLite backend.

## Features
- Add tasks
- Delete tasks
- Mark tasks as completed (toggle)

## Setup

It's recommended to use a Python virtual environment. If `python -m venv venv` fails (e.g. missing `python3-venv` on Linux), install the system package or create an environment manually. The project will work with the system Python as well.

```bash
python -m venv venv          # create venv (may require additional system packages)
source venv/bin/activate
pip install -r requirements.txt
python app.py
```

Alternatively, simply install dependencies globally with `pip install -r requirements.txt` and run `python app.py`.

Then open http://127.0.0.1:5000 in your browser.

## Testing

The project includes comprehensive unit and integration tests using pytest with 80%+ code coverage.

### Run Tests

```bash
# Run all tests
pytest tests/

# Run tests with coverage report (terminal)
pytest tests/ --cov=app --cov-report=term

# Run tests with HTML coverage report
pytest tests/ --cov=app --cov-report=html --cov-report=term
```

### View Coverage Report

After running tests with HTML report, open the browser and navigate to:
```
htmlcov/index.html
```

### Test Structure

- `tests/conftest.py` - Shared fixtures for Flask app and database
- `tests/test_models.py` - Unit tests for the Task model
- `tests/test_routes.py` - Integration tests for all routes

### Coverage Target

Current coverage: **80%+** of `app.py`

Tests cover:
- Task model creation and management
- All 5 routes: GET /, POST /add, GET /delete/<id>, GET /toggle/<id>, GET /delete-completed
- Edge cases: empty inputs, non-existent IDs, special characters, multiple operations
