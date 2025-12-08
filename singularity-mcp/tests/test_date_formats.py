#!/usr/bin/env python3
"""
Test script to check different date formats for SingularityApp API
"""

import asyncio
import os
import sys
from datetime import datetime, date

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Import API directly without going through __init__.py
from singularity_mcp.api import SingularityAPI


async def test_date_formats():
    # Get API token from environment
    token = os.environ.get("SINGULARITY_API_TOKEN")
    if not token:
        print("Error: SINGULARITY_API_TOKEN environment variable is not set")
        return

    api = SingularityAPI(token)

    print("=" * 60)
    print("Testing different date formats for getting today's tasks")
    print("=" * 60)
    print(f"Today's date: {date.today()}")
    print()

    # Test 1: Full ISO format with time (current implementation)
    print("TEST 1: Full ISO format with time (current implementation)")
    print("-" * 40)
    today_start_iso = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0).isoformat()
    today_end_iso = datetime.now().replace(hour=23, minute=59, second=59, microsecond=999999).isoformat()
    print(f"  startDateFrom: {today_start_iso}")
    print(f"  startDateTo: {today_end_iso}")

    try:
        tasks_iso = await api.list_tasks(
            start_date_from=today_start_iso,
            start_date_to=today_end_iso,
            include_archived=False
        )
        print(f"  Result: {len(tasks_iso)} tasks found")
        if tasks_iso:
            print(f"  First task: {tasks_iso[0].get('title', 'No title')}")
            print(f"    Start date: {tasks_iso[0].get('start', 'No start date')}")
    except Exception as e:
        print(f"  ERROR: {e}")
    print()

    # Test 2: Date only format (YYYY-MM-DD) as per documentation
    print("TEST 2: Date only format (YYYY-MM-DD) as per documentation")
    print("-" * 40)
    today_date_only = date.today().isoformat()  # Returns YYYY-MM-DD
    print(f"  startDateFrom: {today_date_only}")
    print(f"  startDateTo: {today_date_only}")

    try:
        tasks_date = await api.list_tasks(
            start_date_from=today_date_only,
            start_date_to=today_date_only,
            include_archived=False
        )
        print(f"  Result: {len(tasks_date)} tasks found")
        if tasks_date:
            print(f"  First task: {tasks_date[0].get('title', 'No title')}")
            print(f"    Start date: {tasks_date[0].get('start', 'No start date')}")
    except Exception as e:
        print(f"  ERROR: {e}")
    print()

    # Test 3: All tasks (no date filter)
    print("TEST 3: All tasks (no date filter)")
    print("-" * 40)

    try:
        all_tasks = await api.list_tasks(
            include_archived=False,
            max_count=10
        )
        print(f"  Result: {len(all_tasks)} tasks found (max 10)")
        if all_tasks:
            print("\n  Tasks with dates:")
            for task in all_tasks[:5]:  # Show first 5
                title = task.get('title', 'No title')
                start = task.get('start', 'No start date')
                print(f"    - {title}")
                print(f"      Start: {start}")
    except Exception as e:
        print(f"  ERROR: {e}")
    print()

    # Test 4: Test with different date formats
    print("TEST 4: Testing edge cases")
    print("-" * 40)

    # Try tomorrow
    from datetime import timedelta
    tomorrow = (date.today() + timedelta(days=1)).isoformat()
    print(f"  Tomorrow ({tomorrow}):")

    try:
        tasks_tomorrow = await api.list_tasks(
            start_date_from=tomorrow,
            start_date_to=tomorrow,
            include_archived=False
        )
        print(f"    Result: {len(tasks_tomorrow)} tasks found")
    except Exception as e:
        print(f"    ERROR: {e}")

    # Try yesterday
    yesterday = (date.today() - timedelta(days=1)).isoformat()
    print(f"  Yesterday ({yesterday}):")

    try:
        tasks_yesterday = await api.list_tasks(
            start_date_from=yesterday,
            start_date_to=yesterday,
            include_archived=False
        )
        print(f"    Result: {len(tasks_yesterday)} tasks found")
    except Exception as e:
        print(f"    ERROR: {e}")

    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"ISO format with time: {len(tasks_iso) if 'tasks_iso' in locals() else 'Failed'} tasks")
    print(f"Date only format: {len(tasks_date) if 'tasks_date' in locals() else 'Failed'} tasks")
    print(f"All tasks: {len(all_tasks) if 'all_tasks' in locals() else 'Failed'} tasks")

    if 'tasks_date' in locals() and len(tasks_date) > 0:
        print("\n✅ Date only format (YYYY-MM-DD) seems to work correctly!")
        print("This is the format that should be used according to the documentation.")
    elif 'tasks_iso' in locals() and len(tasks_iso) > 0:
        print("\n⚠️ ISO format with time works, but may not be the recommended format.")
    else:
        print("\n❌ No tasks found with either format.")
        print("Possible reasons:")
        print("  1. You really don't have tasks scheduled for today")
        print("  2. Tasks might use a different date field")
        print("  3. API might require different parameters")


if __name__ == "__main__":
    asyncio.run(test_date_formats())