#!/usr/bin/env python3
"""
Test script to verify the fix for getting today's tasks
"""

import os
import sys
import json
from datetime import datetime, timedelta

def test_with_curl():
    """Test using curl with the exact parameters from our fix"""
    print("=" * 60)
    print("Testing with CURL")
    print("=" * 60)

    # Get token from environment
    token = os.environ.get("SINGULARITY_API_TOKEN", "34c737d2-5237-438b-97dc-a83ec77db36e")

    # Calculate dates like in our fix
    today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0).isoformat()
    tomorrow_start = (datetime.now() + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0).isoformat()

    print(f"Date range: {today_start} to {tomorrow_start}")
    print(f"includeAllRecurrenceInstances: false")
    print()

    # Build the curl command
    url = (
        f"https://api.singularity-app.com/v2/task"
        f"?includeRemoved=false"
        f"&includeArchived=false"
        f"&includeAllRecurrenceInstances=false"
        f"&startDateFrom={today_start}"
        f"&startDateTo={tomorrow_start}"
    )

    curl_cmd = f'''curl -s -X GET "{url}" -H "accept: application/json" -H "Authorization: Bearer {token}"'''

    print("Executing curl request...")
    result = os.popen(curl_cmd).read()

    try:
        response = json.loads(result)
        # API returns {"tasks": [...]} format
        if isinstance(response, dict) and 'tasks' in response:
            tasks = response['tasks']
            print(f"\n✅ Success! Found {len(tasks)} tasks for today")
            if tasks:
                print("\nFirst 3 tasks:")
                for i, task in enumerate(tasks[:3], 1):
                    print(f"  {i}. {task.get('title', 'No title')}")
                    print(f"     Start: {task.get('start', 'No start date')}")
        elif isinstance(response, list):
            # Just in case API returns list directly
            tasks = response
            print(f"\n✅ Success! Found {len(tasks)} tasks for today")
            if tasks:
                print("\nFirst 3 tasks:")
                for i, task in enumerate(tasks[:3], 1):
                    print(f"  {i}. {task.get('title', 'No title')}")
                    print(f"     Start: {task.get('start', 'No start date')}")
        else:
            print(f"\n❌ Unexpected response type: {type(response)}")
            print(f"Response: {response}")
    except json.JSONDecodeError as e:
        print(f"\n❌ Failed to parse JSON response: {e}")
        print(f"Raw response: {result[:500]}")
    except Exception as e:
        print(f"\n❌ Error: {e}")

    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"Today start: {today_start}")
    print(f"Tomorrow start (used as end): {tomorrow_start}")
    print(f"includeAllRecurrenceInstances: false")
    print("\nThis is the exact configuration used in the fix.")

if __name__ == "__main__":
    test_with_curl()