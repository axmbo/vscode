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
