#!/usr/bin/env python3
"""
Test timezone functionality for SingularityApp MCP server
"""

import asyncio
import os
import sys
from datetime import datetime, timezone, timedelta

# Add src to path to import API directly
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src', 'singularity_mcp'))

# Use urllib for HTTP requests (part of standard library)
import json
import urllib.request
import urllib.parse
from typing import Any

class SingularityAPI:
    """Client for SingularityApp API v2"""

    BASE_URL = "https://api.singularity-app.com/v2"

    def __init__(self, token: str):
        self.token = token
        self.headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }

    async def _request(
        self,
        method: str,
        endpoint: str,
        params: dict | None = None,
        json_data: dict | None = None,
    ) -> dict | list | None:
        """Make an API request using urllib"""
        url = f"{self.BASE_URL}{endpoint}"

        if params:
            url = f"{url}?{urllib.parse.urlencode(params)}"

        request = urllib.request.Request(url, headers=self.headers)
        request.get_method = lambda: method

        if json_data:
            request.data = json.dumps(json_data).encode('utf-8')

        try:
            with urllib.request.urlopen(request, timeout=30) as response:
                if response.status == 204:
                    return None
                data = response.read()
                return json.loads(data)
        except urllib.error.HTTPError as e:
            error_msg = e.read().decode('utf-8')
            raise Exception(f"API Error {e.code}: {error_msg}")

    async def list_tasks(
        self,
        project_id: str | None = None,
        include_archived: bool = False,
        include_removed: bool = False,
        include_all_recurrence_instances: bool = False,
        start_date_from: str | None = None,
        start_date_to: str | None = None,
        max_count: int | None = 100,
    ) -> list[dict]:
        """Get list of tasks"""
        params = {
            "includeArchived": str(include_archived).lower(),
            "includeRemoved": str(include_removed).lower(),
            "includeAllRecurrenceInstances": str(include_all_recurrence_instances).lower(),
        }
        if project_id:
            params["projectId"] = project_id
        if start_date_from:
            params["startDateFrom"] = start_date_from
        if start_date_to:
            params["startDateTo"] = start_date_to
        if max_count:
            params["maxCount"] = str(max_count)

        result = await self._request("GET", "/task", params=params)

        # API returns {"tasks": [...]} format
        if isinstance(result, dict) and 'tasks' in result:
            return result['tasks']
        elif isinstance(result, list):
            return result
        else:
            return []


def get_timezone_offset() -> int:
    """Get timezone offset from environment or default to UTC+3"""
    tz_offset = os.environ.get("SINGULARITY_TIMEZONE_OFFSET", "3")
    try:
        return int(tz_offset)
    except ValueError:
        print(f"Invalid SINGULARITY_TIMEZONE_OFFSET: {tz_offset}, using UTC+3")
        return 3


def get_today_range_utc():
    """Get today's date range in UTC, adjusted for local timezone"""
    tz_offset = get_timezone_offset()
    local_tz = timezone(timedelta(hours=tz_offset))

    # Get "today" in local timezone
    now_local = datetime.now(local_tz)
    today_start_local = now_local.replace(hour=0, minute=0, second=0, microsecond=0)
    tomorrow_start_local = today_start_local + timedelta(days=1)

    # Convert to UTC
    today_start_utc = today_start_local.astimezone(timezone.utc)
    tomorrow_start_utc = tomorrow_start_local.astimezone(timezone.utc)

    return today_start_utc, tomorrow_start_utc


async def test_timezone_conversion():
    """Test timezone conversion for today's tasks"""
    print("=" * 60)
    print("Testing Timezone Conversion for Task Filtering")
    print("=" * 60)

    # Get timezone offset
    tz_offset = get_timezone_offset()
    print(f"\nTimezone Offset: UTC+{tz_offset}")

    # Show local time
    local_tz = timezone(timedelta(hours=tz_offset))
    now_local = datetime.now(local_tz)
    print(f"Current Local Time: {now_local.isoformat()}")

    # Show "today" in local timezone
    today_start_local = now_local.replace(hour=0, minute=0, second=0, microsecond=0)
    tomorrow_start_local = today_start_local + timedelta(days=1)
    print(f"\nLocal 'Today' Range:")
    print(f"  Start: {today_start_local.isoformat()}")
    print(f"  End:   {tomorrow_start_local.isoformat()}")

    # Get UTC range for API
    today_start_utc, tomorrow_start_utc = get_today_range_utc()
    print(f"\nUTC Range for API (to get local 'today'):")
    print(f"  Start: {today_start_utc.isoformat()}")
    print(f"  End:   {tomorrow_start_utc.isoformat()}")

    # Show the difference
    print(f"\nTime Difference:")
    print(f"  Local midnight = UTC {today_start_utc.strftime('%H:%M')} (previous day if negative)")
    print(f"  This means: to get tasks for 'today' in UTC+{tz_offset},")
    print(f"  we need to search from {today_start_utc.strftime('%Y-%m-%d %H:%M UTC')}")
    print(f"  to {tomorrow_start_utc.strftime('%Y-%m-%d %H:%M UTC')}")


async def test_api_with_timezone():
    """Test actual API calls with timezone conversion"""
    token = os.environ.get("SINGULARITY_API_TOKEN")
    if not token:
        print("\n⚠️  SINGULARITY_API_TOKEN not set, skipping API test")
        return

    print("\n" + "=" * 60)
    print("Testing API with Timezone Conversion")
    print("=" * 60)

    api = SingularityAPI(token)

    # Get today's range in UTC
    today_start_utc, tomorrow_start_utc = get_today_range_utc()

    print(f"\nFetching tasks for local 'today' using UTC range:")
    print(f"  From: {today_start_utc.isoformat()}")
    print(f"  To:   {tomorrow_start_utc.isoformat()}")

    try:
        tasks = await api.list_tasks(
            start_date_from=today_start_utc.isoformat(),
            start_date_to=tomorrow_start_utc.isoformat(),
            include_all_recurrence_instances=False,
        )

        print(f"\n✅ Found {len(tasks)} tasks for today")

        if tasks:
            print("\nSample tasks (first 3):")
            for i, task in enumerate(tasks[:3], 1):
                title = task.get('title', 'No title')
                start = task.get('start', 'No start date')
                print(f"  {i}. {title}")
                print(f"     Start (UTC): {start}")

                # Convert to local time for display
                if start and start != 'No start date':
                    dt_utc = datetime.fromisoformat(start.replace('Z', '+00:00'))
                    tz_offset = get_timezone_offset()
                    local_tz = timezone(timedelta(hours=tz_offset))
                    dt_local = dt_utc.astimezone(local_tz)
                    print(f"     Start (Local): {dt_local.isoformat()}")

    except Exception as e:
        print(f"\n❌ API Error: {e}")


async def main():
    # Test timezone conversion logic
    await test_timezone_conversion()

    # Test with actual API
    await test_api_with_timezone()

    print("\n" + "=" * 60)
    print("Test Complete")
    print("=" * 60)

    # Show usage instructions
    print("\n📝 Usage Instructions:")
    print("1. Set timezone offset (default is UTC+3):")
    print("   export SINGULARITY_TIMEZONE_OFFSET=3")
    print("")
    print("2. Set your Singularity API token:")
    print("   export SINGULARITY_API_TOKEN=your-token-here")
    print("")
    print("3. Run this test:")
    print("   python test_timezone.py")


if __name__ == "__main__":
    asyncio.run(main())