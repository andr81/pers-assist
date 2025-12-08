#!/usr/bin/env python3
"""
Simple test to check today's tasks filtering with correct date format
"""

import asyncio
import os
import sys
from datetime import datetime

# Add src to path and import API directly
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src', 'singularity_mcp'))

# Direct import to avoid mcp dependency issues
import httpx
from typing import Any

class TestSingularityAPI:
    """Simplified API client for testing"""
    BASE_URL = "https://api.singularity-app.com/v2"

    def __init__(self, token: str):
        self.token = token
        self.headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }

    async def get_today_tasks(self):
        """Get tasks for today using correct ISO format"""
        # Use full ISO 8601 format with time
        today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0).isoformat()
        today_end = datetime.now().replace(hour=23, minute=59, second=59, microsecond=999999).isoformat()

        print(f"Getting tasks for today:")
        print(f"  Start: {today_start}")
        print(f"  End: {today_end}")

        params = {
            "startDateFrom": today_start,
            "startDateTo": today_end,
            "includeArchived": "false",
            "includeRemoved": "false",
            "maxCount": "100"
        }

        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.BASE_URL}/task",
                headers=self.headers,
                params=params,
                timeout=30.0
            )
            response.raise_for_status()
            return response.json()


async def main():
    # Get token from environment
    token = os.environ.get("SINGULARITY_API_TOKEN")
    if not token:
        print("Error: SINGULARITY_API_TOKEN environment variable is not set")
        return

    api = TestSingularityAPI(token)

    print("=" * 60)
    print("Testing get_today_tasks with correct ISO 8601 format")
    print("=" * 60)

    try:
        tasks = await api.get_today_tasks()
        print(f"\n✅ Success! Found {len(tasks)} tasks for today")

        if tasks:
            print("\nTasks found:")
            for i, task in enumerate(tasks[:5], 1):  # Show first 5 tasks
                title = task.get('title', 'No title')
                start = task.get('start', 'No start date')
                print(f"  {i}. {title}")
                print(f"     Start: {start}")
        else:
            print("\nNo tasks scheduled for today.")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())