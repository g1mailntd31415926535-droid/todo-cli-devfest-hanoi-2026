#!/usr/bin/env python3
"""CLI task tracker using only Python standard library."""

import argparse
import json
import os
import sys
from typing import Any, Dict, List, Optional

DEFAULT_FILENAME = "tasks.json"


def load_tasks(filepath: str = DEFAULT_FILENAME) -> List[Dict[str, Any]]:
    """Load tasks from a JSON file. Returns empty list if file doesn't exist."""
    if not os.path.exists(filepath):
        return []
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
            if isinstance(data, list):
                return data
            return []
    except (json.JSONDecodeError, OSError):
        return []


def save_tasks(tasks: List[Dict[str, Any]], filepath: str = DEFAULT_FILENAME) -> None:
    """Save tasks list to a JSON file."""
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(tasks, f, indent=2)


def add_task(title: str, filepath: str = DEFAULT_FILENAME) -> Dict[str, Any]:
    """Add a new task with given title and save it."""
    tasks = load_tasks(filepath)
    next_id = max((t.get("id", 0) for t in tasks), default=0) + 1
    new_task = {
        "id": next_id,
        "title": title,
        "completed": False,
    }
    tasks.append(new_task)
    save_tasks(tasks, filepath)
    return new_task


def list_tasks(filepath: str = DEFAULT_FILENAME) -> List[Dict[str, Any]]:
    """Return all tasks."""
    return load_tasks(filepath)


def complete_task(task_id: int, filepath: str = DEFAULT_FILENAME) -> Optional[Dict[str, Any]]:
    """Mark a task as completed by ID. Return updated task or None if not found."""
    tasks = load_tasks(filepath)
    for task in tasks:
        if task.get("id") == task_id:
            task["completed"] = True
            save_tasks(tasks, filepath)
            return task
    return None


def build_parser() -> argparse.ArgumentParser:
    """Build and return command line argument parser."""
    parser = argparse.ArgumentParser(
        prog="todo",
        description="A simple CLI task tracker",
    )
    parser.add_argument(
        "--file",
        default=DEFAULT_FILENAME,
        help=f"Tasks file path (default: {DEFAULT_FILENAME})",
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Add command
    add_parser = subparsers.add_parser("add", help="Add a new task")
    add_parser.add_argument("title", help="Title / description of the task")

    # List command
    subparsers.add_parser("list", help="List all tasks")

    # Complete command
    complete_parser = subparsers.add_parser("complete", help="Complete a task by ID")
    complete_parser.add_argument("id", type=int, help="Task ID to mark complete")

    return parser


def main(argv: Optional[List[str]] = None) -> int:
    """Main CLI entrypoint."""
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "add":
        task = add_task(args.title, filepath=args.file)
        print(f"Task added [ID: {task['id']}]: {task['title']}")
        return 0

    elif args.command == "list":
        tasks = list_tasks(filepath=args.file)
        if not tasks:
            print("No tasks found.")
            return 0
        for task in tasks:
            status = "[x]" if task.get("completed") else "[ ]"
            print(f"{task.get('id')}. {status} {task.get('title')}")
        return 0

    elif args.command == "complete":
        task = complete_task(args.id, filepath=args.file)
        if task:
            print(f"Task {task['id']} marked as completed: {task['title']}")
            return 0
        else:
            print(f"Error: Task with ID {args.id} not found.", file=sys.stderr)
            return 1

    else:
        parser.print_help()
        return 0


if __name__ == "__main__":
    sys.exit(main())
