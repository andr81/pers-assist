#!/usr/bin/env python3
"""
Test script for creating a task with project_id
"""

import asyncio
import os
import sys
from datetime import datetime

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from singularity_mcp.api import SingularityAPI


async def main():
    # Get API token from environment
    token = os.environ.get("SINGULARITY_API_TOKEN")
    if not token:
        print("Error: SINGULARITY_API_TOKEN environment variable is not set")
        return

    api = SingularityAPI(token)

    # First, list projects to get a valid project_id
    print("\n=== Listing Projects ===")
    try:
        projects = await api.list_projects()
        if not projects:
            print("No projects found. Please create a project first.")
            return

        print(f"Found {len(projects)} projects:")
        for project in projects[:5]:  # Show first 5 projects
            print(f"  - {project.get('id')}: {project.get('title')}")

        # Use the first project for testing
        test_project_id = projects[0].get('id')
        print(f"\nUsing project: {test_project_id}")

    except Exception as e:
        print(f"Error listing projects: {e}")
        return

    # Test creating a task with project_id
    print("\n=== Creating Task with Project ===")
    try:
        task_title = f"Test task with project - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        task_start = datetime.now().replace(hour=10, minute=0, second=0, microsecond=0).isoformat()

        print(f"Creating task:")
        print(f"  Title: {task_title}")
        print(f"  Project ID: {test_project_id}")
        print(f"  Start: {task_start}")
        print(f"  Priority: 1 (normal)")

        result = await api.create_task(
            title=task_title,
            project_id=test_project_id,
            start=task_start,
            note="This is a test task created with a specific project",
            priority=1
        )

        print(f"\nTask created successfully!")
        print(f"  Task ID: {result.get('id')}")
        print(f"  Project in result: {result.get('project')}")

        # Verify the task has the correct project
        if result.get('project') == test_project_id:
            print("\n✅ SUCCESS: Task was created with the correct project!")
        else:
            print(f"\n❌ ERROR: Task project doesn't match! Expected {test_project_id}, got {result.get('project')}")

    except Exception as e:
        print(f"Error creating task: {e}")
        import traceback
        traceback.print_exc()

    # Test creating a task WITHOUT project_id
    print("\n=== Creating Task without Project ===")
    try:
        task_title = f"Test task without project - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"

        print(f"Creating task:")
        print(f"  Title: {task_title}")
        print(f"  Project ID: None")

        result = await api.create_task(
            title=task_title,
            note="This task should be created without a project (in Inbox)"
        )

        print(f"\nTask created successfully!")
        print(f"  Task ID: {result.get('id')}")
        print(f"  Project in result: {result.get('project')}")

        if result.get('project') is None:
            print("\n✅ SUCCESS: Task was created without a project (in Inbox)!")
        else:
            print(f"\n❌ ERROR: Task has unexpected project: {result.get('project')}")

    except Exception as e:
        print(f"Error creating task: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())