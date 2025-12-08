#!/usr/bin/env python3
"""
Simple test using built-in libraries
"""

import json
import urllib.request
import urllib.parse
import os
from datetime import datetime


def test_today_tasks():
    """Test getting today's tasks with correct date format"""

    # Get token from environment
    token = os.environ.get("SINGULARITY_API_TOKEN")
    if not token:
        print("Error: SINGULARITY_API_TOKEN environment variable is not set")
        return

    # Use full ISO 8601 format with time
    today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0).isoformat()
    today_end = datetime.now().replace(hour=23, minute=59, second=59, microsecond=999999).isoformat()

    print("=" * 60)
    print("Testing SingularityApp API - Get Today's Tasks")
    print("=" * 60)
    print(f"\nDate range:")
    print(f"  From: {today_start}")
    print(f"  To: {today_end}")

    # Build URL with parameters
    base_url = "https://api.singularity-app.com/v2/task"
    params = {
        "startDateFrom": today_start,
        "startDateTo": today_end,
        "includeArchived": "false",
        "includeRemoved": "false",
        "maxCount": "100"
    }
    url = f"{base_url}?{urllib.parse.urlencode(params)}"

    # Create request with headers
    request = urllib.request.Request(url)
    request.add_header("Authorization", f"Bearer {token}")
    request.add_header("Content-Type", "application/json")

    try:
        # Make the request
        with urllib.request.urlopen(request) as response:
            data = json.loads(response.read().decode())

        print(f"\n✅ Success! Found {len(data)} tasks for today")

        if data:
            print("\nTasks found:")
            for i, task in enumerate(data[:5], 1):  # Show first 5 tasks
                title = task.get('title', 'No title')
                start = task.get('start', 'No start date')
                task_id = task.get('id', 'No ID')
                print(f"  {i}. [{task_id}] {title}")
                print(f"     Start: {start}")
        else:
            print("\nNo tasks scheduled for today.")
            print("\nTip: To test, you can create a task for today using the API")

    except urllib.error.HTTPError as e:
        print(f"\n❌ HTTP Error {e.code}: {e.reason}")
        try:
            error_data = json.loads(e.read().decode())
            print(f"Error details: {json.dumps(error_data, indent=2)}")
        except:
            pass
    except Exception as e:
        print(f"\n❌ Error: {e}")


if __name__ == "__main__":
    test_today_tasks()