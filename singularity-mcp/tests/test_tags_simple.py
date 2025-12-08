#!/usr/bin/env python3
"""
Simple test script for SingularityApp tags API (without MCP dependencies)
"""

import asyncio
import httpx
from datetime import datetime
import json


async def test_tags_api():
    """Test tags functionality directly via API"""

    TOKEN = "34c737d2-5237-438b-97dc-a83ec77db36e"
    BASE_URL = "https://api.singularity-app.com/v2"

    headers = {
        "Authorization": f"Bearer {TOKEN}",
        "Content-Type": "application/json",
        "accept": "application/json"
    }

    print("\n=== Testing Tags API ===\n")

    async with httpx.AsyncClient() as client:
        try:
            # 1. List tags
            print("1. Getting list of tags...")
            response = await client.get(
                f"{BASE_URL}/tag",
                headers=headers,
                params={"includeRemoved": "false"}
            )

            if response.status_code == 200:
                data = response.json()

                # Handle both formats: {"tags": [...]} or direct list
                if isinstance(data, dict) and 'tags' in data:
                    tags = data['tags']
                elif isinstance(data, list):
                    tags = data
                else:
                    tags = []

                print(f"   Found {len(tags)} tags")

                # Show existing tags
                if tags:
                    print("\n   Existing tags:")
                    for tag in tags[:10]:
                        tag_id = tag.get('id', 'N/A')
                        title = tag.get('title', 'Untitled')
                        print(f"   - {tag_id}: {title}")

                    if len(tags) > 10:
                        print(f"   ... and {len(tags) - 10} more")
            else:
                print(f"   Error: {response.status_code} - {response.text}")
                return

            # 2. Create a test tag
            print("\n2. Creating a test tag...")
            test_tag_title = f"Test Tag {datetime.now().strftime('%H:%M:%S')}"

            response = await client.post(
                f"{BASE_URL}/tag",
                headers=headers,
                json={"title": test_tag_title}
            )

            if response.status_code in [200, 201]:
                new_tag = response.json()
                tag_id = new_tag.get('id')
                print(f"   Created tag: {tag_id} - {test_tag_title}")
            else:
                print(f"   Error creating tag: {response.status_code} - {response.text}")
                return

            # 3. Get tag details
            if tag_id:
                print(f"\n3. Getting details for tag {tag_id}...")
                response = await client.get(
                    f"{BASE_URL}/tag/{tag_id}",
                    headers=headers
                )

                if response.status_code == 200:
                    tag_details = response.json()
                    print(f"   ID: {tag_details.get('id')}")
                    print(f"   Title: {tag_details.get('title')}")
                    print(f"   Created: {tag_details.get('createdDate', 'N/A')}")
                else:
                    print(f"   Error: {response.status_code}")

            # 4. Update tag
            if tag_id:
                print(f"\n4. Updating tag {tag_id}...")
                updated_title = f"Updated {test_tag_title}"

                response = await client.patch(
                    f"{BASE_URL}/tag/{tag_id}",
                    headers=headers,
                    json={"title": updated_title}
                )

                if response.status_code == 200:
                    print(f"   Updated title to: {updated_title}")
                else:
                    print(f"   Error: {response.status_code}")

            # 5. Test with tasks
            print("\n5. Testing tags with tasks...")

            # Get a task
            response = await client.get(
                f"{BASE_URL}/task",
                headers=headers,
                params={
                    "includeArchived": "false",
                    "includeRemoved": "false",
                    "maxCount": "1"
                }
            )

            if response.status_code == 200:
                task_data = response.json()

                # Handle response format
                if isinstance(task_data, dict) and 'tasks' in task_data:
                    tasks = task_data['tasks']
                elif isinstance(task_data, list):
                    tasks = task_data
                else:
                    tasks = []

                if tasks and tag_id:
                    task = tasks[0]
                    task_id = task.get('id')
                    task_title = task.get('title', 'Untitled')
                    current_tags = task.get('tags', [])

                    print(f"   Using task: {task_id}")
                    print(f"   Title: {task_title}")
                    print(f"   Current tags: {current_tags}")

                    # Add tag to task
                    print(f"\n6. Adding tag {tag_id} to task...")
                    new_tags = current_tags.copy()
                    if tag_id not in new_tags:
                        new_tags.append(tag_id)

                    response = await client.patch(
                        f"{BASE_URL}/task/{task_id}",
                        headers=headers,
                        json={"tags": new_tags}
                    )

                    if response.status_code == 200:
                        print(f"   Successfully added tag to task")
                        updated_task = response.json()
                        print(f"   Task tags now: {updated_task.get('tags', [])}")

                        # Remove tag
                        print(f"\n7. Removing tag {tag_id} from task...")
                        response = await client.patch(
                            f"{BASE_URL}/task/{task_id}",
                            headers=headers,
                            json={"tags": current_tags}
                        )

                        if response.status_code == 200:
                            print("   Successfully removed tag from task")
                    else:
                        print(f"   Error adding tag: {response.status_code}")

            # 6. Delete test tag
            if tag_id:
                print(f"\n8. Deleting test tag {tag_id}...")
                response = await client.delete(
                    f"{BASE_URL}/tag/{tag_id}",
                    headers=headers
                )

                if response.status_code in [200, 204]:
                    print("   Tag deleted successfully")
                else:
                    print(f"   Error deleting: {response.status_code}")

            print("\n=== Tests completed! ===\n")

        except Exception as e:
            print(f"\nError during testing: {e}")
            import traceback
            traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_tags_api())