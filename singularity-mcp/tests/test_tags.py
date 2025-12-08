#!/usr/bin/env python3
"""
Test script for SingularityApp MCP tags functionality
"""

import asyncio
import os
import sys
from datetime import datetime

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from singularity_mcp.api import SingularityAPI


async def test_tags():
    """Test tags functionality"""

    # Get API token from environment
    token = os.environ.get("SINGULARITY_API_TOKEN")
    if not token:
        print("ERROR: SINGULARITY_API_TOKEN environment variable is required")
        print("Get your token at https://me.singularity-app.com")
        return

    api = SingularityAPI(token)

    print("\n=== Testing Tags Functionality ===\n")

    try:
        # 1. List all tags
        print("1. Listing all tags...")
        tags = await api.list_tags()
        print(f"   Found {len(tags)} tags")

        if tags:
            # Show first few tags
            for i, tag in enumerate(tags[:5]):
                print(f"   - {tag.get('id', 'N/A')}: {tag.get('title', 'Untitled')}")
                if tag.get('parent'):
                    print(f"     Parent: {tag['parent']}")

            if len(tags) > 5:
                print(f"   ... and {len(tags) - 5} more")
        else:
            print("   No tags found")

        # 2. Create a test tag
        print("\n2. Creating a test tag...")
        test_tag_title = f"Test Tag {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        new_tag = await api.create_tag(title=test_tag_title)
        tag_id = new_tag.get('id')
        print(f"   Created tag: {tag_id} - {test_tag_title}")

        # 3. Get tag details
        print(f"\n3. Getting tag details for {tag_id}...")
        tag_details = await api.get_tag(tag_id)
        print(f"   ID: {tag_details.get('id')}")
        print(f"   Title: {tag_details.get('title')}")
        print(f"   Created: {tag_details.get('createdDate', 'N/A')}")

        # 4. Update tag
        print(f"\n4. Updating tag {tag_id}...")
        updated_title = f"Updated {test_tag_title}"
        updated_tag = await api.update_tag(tag_id, title=updated_title)
        print(f"   Updated title to: {updated_title}")

        # 5. Find a task to test with
        print("\n5. Finding a task to test tag operations...")
        tasks = await api.list_tasks(max_count=5)

        if tasks:
            test_task = tasks[0]
            task_id = test_task.get('id')
            task_title = test_task.get('title', 'Untitled')
            current_tags = test_task.get('tags', [])

            print(f"   Using task: {task_id} - {task_title}")
            print(f"   Current tags: {current_tags}")

            # 6. Add tag to task
            print(f"\n6. Adding tag {tag_id} to task {task_id}...")
            updated_task = await api.add_task_tag(task_id, tag_id)
            new_tags = updated_task.get('tags', [])
            print(f"   Task tags after adding: {new_tags}")

            # 7. List tasks with this tag
            print(f"\n7. Listing tasks with tag {tag_id}...")
            tagged_tasks = await api.list_tasks(tag_ids=[tag_id])
            print(f"   Found {len(tagged_tasks)} tasks with this tag")
            for task in tagged_tasks[:3]:
                print(f"   - {task.get('id')}: {task.get('title', 'Untitled')}")

            # 8. Remove tag from task
            print(f"\n8. Removing tag {tag_id} from task {task_id}...")
            updated_task = await api.remove_task_tag(task_id, tag_id)
            final_tags = updated_task.get('tags', [])
            print(f"   Task tags after removal: {final_tags}")
        else:
            print("   No tasks found for testing")

        # 9. Delete test tag
        print(f"\n9. Deleting test tag {tag_id}...")
        await api.delete_tag(tag_id)
        print("   Tag deleted successfully")

        # 10. Verify deletion
        print("\n10. Verifying tag deletion...")
        try:
            deleted_tag = await api.get_tag(tag_id)
            print(f"   WARNING: Tag still exists: {deleted_tag}")
        except Exception as e:
            print(f"   Tag successfully deleted (error expected): {str(e)[:50]}...")

        print("\n=== All tests completed successfully! ===\n")

    except Exception as e:
        print(f"\n!!! Error during testing: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_tags())