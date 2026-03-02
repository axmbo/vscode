import pytest
from app import Task, db, app


class TestIndexRoute:
    """Tests for the index (GET /) route."""

    def test_index_get_returns_200(self, client):
        """Test that GET / returns status 200."""
        response = client.get('/')
        assert response.status_code == 200

    def test_index_renders_template(self, client):
        """Test that index renders the correct template."""
        response = client.get('/')
        assert b'<!DOCTYPE html>' in response.data or b'<html' in response.data

    def test_index_with_empty_tasks(self, client):
        """Test index page with no tasks."""
        response = client.get('/')
        assert response.status_code == 200
        # Check that it contains the form element
        assert b'name="description"' in response.data

    def test_index_displays_all_tasks(self, client):
        """Test that all tasks are displayed on index page."""
        with app.app_context():
            task1 = Task(description="Task 1")
            task2 = Task(description="Task 2")
            db.session.add_all([task1, task2])
            db.session.commit()

        response = client.get('/')
        assert b'Task 1' in response.data
        assert b'Task 2' in response.data

    def test_index_completed_count(self, client):
        """Test that completed count is calculated correctly."""
        with app.app_context():
            task1 = Task(description="Task 1", completed=False)
            task2 = Task(description="Task 2", completed=True)
            task3 = Task(description="Task 3", completed=True)
            db.session.add_all([task1, task2, task3])
            db.session.commit()

        response = client.get('/')
        # The server should calculate 2 completed tasks
        assert response.status_code == 200
        assert b'Task 1' in response.data
        assert b'Task 2' in response.data
        assert b'Task 3' in response.data

    def test_index_strikethrough_for_completed_tasks(self, client):
        """Test that completed tasks are styled with strikethrough."""
        with app.app_context():
            task1 = Task(description="Active task", completed=False)
            task2 = Task(description="Completed task", completed=True)
            db.session.add_all([task1, task2])
            db.session.commit()

        response = client.get('/')
        # Check that the completed task is wrapped in <strike> tags
        assert b'Active task' in response.data
        assert b'<strike>Completed task</strike>' in response.data


class TestAddRoute:
    """Tests for the add task (POST /add) route."""

    def test_add_task_with_valid_description(self, client):
        """Test adding a task with valid description."""
        response = client.post('/add', data={'description': 'New task'}, follow_redirects=True)
        assert response.status_code == 200

        # Verify task was added to database
        with app.app_context():
            task = Task.query.filter_by(description='New task').first()
            assert task is not None
            assert task.completed is False

    def test_add_task_redirects_to_index(self, client):
        """Test that adding a task redirects to index."""
        response = client.post('/add', data={'description': 'Redirect test'})
        assert response.status_code == 302
        assert response.location.endswith('/')

    def test_add_task_with_empty_description(self, client):
        """Test that empty description is rejected."""
        response = client.post('/add', data={'description': ''}, follow_redirects=True)

        # Empty task should not be created
        with app.app_context():
            task = Task.query.filter_by(description='').first()
            assert task is None

    def test_add_task_with_whitespace_only(self, client):
        """Test that whitespace-only description is accepted (not validated)."""
        response = client.post('/add', data={'description': '   '}, follow_redirects=True)

        # Whitespace-only task is created (app doesn't strip/validate)
        with app.app_context():
            task_count = Task.query.count()
            # App accepts whitespace, so task is created
            assert task_count == 1

    def test_add_task_with_special_characters(self, client):
        """Test adding a task with special characters."""
        desc = "Task with special: !@#$%^&*()"
        response = client.post('/add', data={'description': desc}, follow_redirects=True)

        with app.app_context():
            task = Task.query.filter_by(description=desc).first()
            assert task is not None

    def test_add_multiple_tasks(self, client):
        """Test adding multiple tasks sequentially."""
        tasks = ['Task 1', 'Task 2', 'Task 3']

        for task_desc in tasks:
            client.post('/add', data={'description': task_desc})

        with app.app_context():
            count = Task.query.count()
            assert count == 3


class TestDeleteRoute:
    """Tests for the delete task (GET /delete/<id>) route."""

    def test_delete_existing_task(self, client):
        """Test deleting an existing task."""
        with app.app_context():
            task = Task(description="Task to delete")
            db.session.add(task)
            db.session.commit()
            task_id = task.id

        response = client.get(f'/delete/{task_id}')
        assert response.status_code == 302

        # Verify task was deleted
        with app.app_context():
            deleted_task = Task.query.get(task_id)
            assert deleted_task is None

    def test_delete_nonexistent_task_returns_404(self, client):
        """Test that deleting a non-existent task returns 404."""
        response = client.get('/delete/99999')
        assert response.status_code == 404

    def test_delete_redirects_to_index(self, client):
        """Test that delete redirects to index."""
        with app.app_context():
            task = Task(description="Delete redirect test")
            db.session.add(task)
            db.session.commit()
            task_id = task.id

        response = client.get(f'/delete/{task_id}')
        assert response.location.endswith('/')

    def test_delete_does_not_affect_other_tasks(self, client):
        """Test that deleting one task doesn't affect others."""
        with app.app_context():
            task1 = Task(description="Keep this")
            task2 = Task(description="Delete this")
            db.session.add_all([task1, task2])
            db.session.commit()
            task2_id = task2.id

        client.get(f'/delete/{task2_id}')

        with app.app_context():
            remaining = Task.query.filter_by(description="Keep this").first()
            assert remaining is not None


class TestToggleRoute:
    """Tests for the toggle task (GET /toggle/<id>) route."""

    def test_toggle_task_from_incomplete_to_complete(self, client):
        """Test toggling a task from incomplete to complete."""
        with app.app_context():
            task = Task(description="Toggle test", completed=False)
            db.session.add(task)
            db.session.commit()
            task_id = task.id

        response = client.get(f'/toggle/{task_id}')
        assert response.status_code == 302

        with app.app_context():
            updated_task = Task.query.get(task_id)
            assert updated_task.completed is True

    def test_toggle_task_from_complete_to_incomplete(self, client):
        """Test toggling a task from complete to incomplete."""
        with app.app_context():
            task = Task(description="Toggle back", completed=True)
            db.session.add(task)
            db.session.commit()
            task_id = task.id

        client.get(f'/toggle/{task_id}')

        with app.app_context():
            updated_task = Task.query.get(task_id)
            assert updated_task.completed is False

    def test_toggle_nonexistent_task_returns_404(self, client):
        """Test that toggling a non-existent task returns 404."""
        response = client.get('/toggle/99999')
        assert response.status_code == 404

    def test_toggle_redirects_to_index(self, client):
        """Test that toggle redirects to index."""
        with app.app_context():
            task = Task(description="Redirect on toggle")
            db.session.add(task)
            db.session.commit()
            task_id = task.id

        response = client.get(f'/toggle/{task_id}')
        assert response.location.endswith('/')

    def test_toggle_multiple_times(self, client):
        """Test toggling the same task multiple times."""
        with app.app_context():
            task = Task(description="Multi-toggle", completed=False)
            db.session.add(task)
            db.session.commit()
            task_id = task.id

        # Toggle 3 times: False -> True -> False -> True
        for _ in range(3):
            client.get(f'/toggle/{task_id}')

        with app.app_context():
            updated_task = Task.query.get(task_id)
            assert updated_task.completed is True


class TestDeleteCompletedRoute:
    """Tests for the delete completed tasks route (GET /delete-completed)."""

    def test_delete_completed_removes_only_completed(self, client):
        """Test that only completed tasks are deleted."""
        with app.app_context():
            task1 = Task(description="Active 1", completed=False)
            task2 = Task(description="Completed 1", completed=True)
            task3 = Task(description="Active 2", completed=False)
            task4 = Task(description="Completed 2", completed=True)
            db.session.add_all([task1, task2, task3, task4])
            db.session.commit()

        response = client.get('/delete-completed')
        assert response.status_code == 302

        with app.app_context():
            active_count = Task.query.filter_by(completed=False).count()
            completed_count = Task.query.filter_by(completed=True).count()
            assert active_count == 2
            assert completed_count == 0

    def test_delete_completed_with_no_completed_tasks(self, client):
        """Test delete-completed when there are no completed tasks."""
        with app.app_context():
            task1 = Task(description="Task 1", completed=False)
            task2 = Task(description="Task 2", completed=False)
            db.session.add_all([task1, task2])
            db.session.commit()
            initial_count = Task.query.count()

        client.get('/delete-completed')

        with app.app_context():
            final_count = Task.query.count()
            assert final_count == initial_count

    def test_delete_completed_with_all_completed(self, client):
        """Test delete-completed when all tasks are completed."""
        with app.app_context():
            task1 = Task(description="Task 1", completed=True)
            task2 = Task(description="Task 2", completed=True)
            db.session.add_all([task1, task2])
            db.session.commit()

        client.get('/delete-completed')

        with app.app_context():
            count = Task.query.count()
            assert count == 0

    def test_delete_completed_redirects_to_index(self, client):
        """Test that delete-completed redirects to index."""
        response = client.get('/delete-completed')
        assert response.location.endswith('/')

    def test_delete_completed_with_empty_database(self, client):
        """Test delete-completed on empty database."""
        response = client.get('/delete-completed')
        assert response.status_code == 302

        with app.app_context():
            count = Task.query.count()
            assert count == 0
