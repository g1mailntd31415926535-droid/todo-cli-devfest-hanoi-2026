#!/usr/bin/env python3
"""Unit tests for todo.py CLI task tracker."""

import io
import json
import os
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout

import todo


class TestTodoFunctions(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.tasks_file = os.path.join(self.temp_dir.name, "tasks.json")

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_load_empty_or_missing_file(self):
        tasks = todo.load_tasks(self.tasks_file)
        self.assertEqual(tasks, [])

    def test_add_task(self):
        task1 = todo.add_task("Buy milk", filepath=self.tasks_file)
        self.assertEqual(task1["id"], 1)
        self.assertEqual(task1["title"], "Buy milk")
        self.assertFalse(task1["completed"])

        task2 = todo.add_task("Clean room", filepath=self.tasks_file)
        self.assertEqual(task2["id"], 2)
        self.assertEqual(task2["title"], "Clean room")
        self.assertFalse(task2["completed"])

        all_tasks = todo.list_tasks(filepath=self.tasks_file)
        self.assertEqual(len(all_tasks), 2)
        self.assertEqual(all_tasks[0]["title"], "Buy milk")
        self.assertEqual(all_tasks[1]["title"], "Clean room")

    def test_complete_task(self):
        todo.add_task("Task 1", filepath=self.tasks_file)
        todo.add_task("Task 2", filepath=self.tasks_file)

        updated = todo.complete_task(1, filepath=self.tasks_file)
        self.assertIsNotNone(updated)
        self.assertTrue(updated["completed"])

        # Check persistence
        tasks = todo.list_tasks(filepath=self.tasks_file)
        self.assertTrue(tasks[0]["completed"])
        self.assertFalse(tasks[1]["completed"])

    def test_complete_nonexistent_task(self):
        res = todo.complete_task(999, filepath=self.tasks_file)
        self.assertIsNone(res)

    def test_load_corrupted_json(self):
        with open(self.tasks_file, "w", encoding="utf-8") as f:
            f.write("invalid json content")
        tasks = todo.load_tasks(self.tasks_file)
        self.assertEqual(tasks, [])


class TestTodoCLI(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.tasks_file = os.path.join(self.temp_dir.name, "tasks.json")

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_cli_add_and_list(self):
        out = io.StringIO()
        with redirect_stdout(out):
            code = todo.main(["--file", self.tasks_file, "add", "Test task via CLI"])
        self.assertEqual(code, 0)
        self.assertIn("Task added [ID: 1]: Test task via CLI", out.getvalue())

        out = io.StringIO()
        with redirect_stdout(out):
            code = todo.main(["--file", self.tasks_file, "list"])
        self.assertEqual(code, 0)
        self.assertIn("1. [ ] Test task via CLI", out.getvalue())

    def test_cli_complete(self):
        todo.add_task("Test task", filepath=self.tasks_file)

        out = io.StringIO()
        with redirect_stdout(out):
            code = todo.main(["--file", self.tasks_file, "complete", "1"])
        self.assertEqual(code, 0)
        self.assertIn("Task 1 marked as completed: Test task", out.getvalue())

        out = io.StringIO()
        with redirect_stdout(out):
            todo.main(["--file", self.tasks_file, "list"])
        self.assertIn("1. [x] Test task", out.getvalue())

    def test_cli_complete_not_found(self):
        err = io.StringIO()
        with redirect_stderr(err):
            code = todo.main(["--file", self.tasks_file, "complete", "42"])
        self.assertEqual(code, 1)
        self.assertIn("Task with ID 42 not found", err.getvalue())

    def test_cli_list_empty(self):
        out = io.StringIO()
        with redirect_stdout(out):
            code = todo.main(["--file", self.tasks_file, "list"])
        self.assertEqual(code, 0)
        self.assertIn("No tasks found.", out.getvalue())


if __name__ == "__main__":
    unittest.main()
