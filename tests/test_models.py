import pytest
from app import Task, db, app


class TestTaskModel:
    """Tests for the Task model."""

    def test_task_creation(self, db_session):
        """Test creating a task with description."""
        task = Task(description="Buy groceries")
        db_session.session.add(task)
        db_session.session.commit()

        assert task.id is not None
        assert task.description == "Buy groceries"
        assert task.completed is False

    def test_task_default_completed_is_false(self, db_session):
        """Test that completed defaults to False."""
        task = Task(description="Test task")
        db_session.session.add(task)
        db_session.session.commit()

        retrieved_task = Task.query.first()
        assert retrieved_task.completed is False

    def test_task_repr(self, db_session):
        """Test the string representation of a task."""
        task = Task(description="Sample task")
        assert repr(task) == "<Task Sample task>"

    def test_task_with_special_characters(self, db_session):
        """Test creating a task with special characters."""
        desc = "Task with special chars: !@#$%^&*()"
        task = Task(description=desc)
        db_session.session.add(task)
        db_session.session.commit()

        retrieved_task = Task.query.first()
        assert retrieved_task.description == desc

    def test_task_with_long_description(self, db_session):
        """Test creating a task with a long description."""
        long_desc = "A" * 200  # Maximum length in the model
        task = Task(description=long_desc)
        db_session.session.add(task)
        db_session.session.commit()

        retrieved_task = Task.query.first()
        assert len(retrieved_task.description) == 200

    def test_toggle_completed_status(self, db_session):
        """Test toggling the completed status of a task."""
        task = Task(description="Toggle test")
        db_session.session.add(task)
        db_session.session.commit()

        assert task.completed is False
        task.completed = True
        db_session.session.commit()

        retrieved_task = Task.query.first()
        assert retrieved_task.completed is True
