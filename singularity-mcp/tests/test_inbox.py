#!/usr/bin/env python3
"""Test script for inbox tasks functionality"""

import asyncio
import os
import sys
from datetime import datetime

# Import API directly without going through __init__.py
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src', 'singularity_mcp'))
from api import SingularityAPI


async def main():
    token = os.environ.get("SINGULARITY_API_TOKEN")
    if not token:
        print("Error: SINGULARITY_API_TOKEN not set")
        return

    api = SingularityAPI(token)

    print("\n" + "=" * 60)
    print("Testing Inbox Tasks")
    print("=" * 60)

    # Test 1: Get all inbox tasks
    print("\n[Test 1] Getting all inbox tasks...")
    try:
        inbox_tasks = await api.list_inbox_tasks()
        print(f"✅ Found {len(inbox_tasks)} tasks in Inbox")

        if inbox_tasks:
            print("\nFirst 5 inbox tasks:")
            for i, task in enumerate(inbox_tasks[:5], 1):
                title = task.get('title', 'No title')
                task_id = task.get('id', 'No ID')
                print(f"  {i}. [{task_id}] {title}")
                # Verify no projectId field
                has_project = 'projectId' in task
                status = "❌ ERROR" if has_project else "✅"
                print(f"     {status} ProjectId check")
        else:
            print("\nNo tasks in Inbox. This might be expected if all tasks are in projects.")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

    # Test 2: Verify filtering
    print("\n[Test 2] Comparing with list_tasks...")
    try:
        all_tasks = await api.list_tasks(max_count=200)
        inbox_tasks = await api.list_inbox_tasks(max_count=200)
        tasks_with_project = [t for t in all_tasks if 'projectId' in t]

        print(f"  Total tasks: {len(all_tasks)}")
        print(f"  Tasks with project: {len(tasks_with_project)}")
        print(f"  Tasks in Inbox: {len(inbox_tasks)}")

        if len(tasks_with_project) + len(inbox_tasks) == len(all_tasks):
            print("✅ Filtering works correctly!")
        else:
            print("❌ Mismatch in task counts")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

    print("\n" + "=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
