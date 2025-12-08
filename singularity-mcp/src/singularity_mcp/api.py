"""
SingularityApp API Client
"""

import logging
import httpx
from typing import Any

# Configure logging
logger = logging.getLogger(__name__)


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
        json: dict | None = None,
    ) -> dict | list | None:
        """Make an API request"""
        async with httpx.AsyncClient() as client:
            response = await client.request(
                method=method,
                url=f"{self.BASE_URL}{endpoint}",
                headers=self.headers,
                params=params,
                json=json,
                timeout=30.0,
            )
            response.raise_for_status()
            if response.status_code == 204:
                return None
            return response.json()
    
    # ============ TASKS ============
    
    async def list_tasks(
        self,
        project_id: str | None = None,
        tag_ids: list[str] | None = None,
        include_archived: bool = False,
        include_removed: bool = False,
        include_all_recurrence_instances: bool = False,
        start_date_from: str | None = None,
        start_date_to: str | None = None,
        max_count: int | None = 100,
    ) -> list[dict]:
        """Get list of tasks"""
        logger.info(f"Listing tasks with filters: project_id={project_id}, tag_ids={tag_ids}, "
                   f"start_date_from={start_date_from}, start_date_to={start_date_to}, "
                   f"include_all_recurrence_instances={include_all_recurrence_instances}")

        params = {
            "includeArchived": str(include_archived).lower(),
            "includeRemoved": str(include_removed).lower(),
            "includeAllRecurrenceInstances": str(include_all_recurrence_instances).lower(),
        }
        if project_id:
            params["projectId"] = project_id
        if tag_ids:
            # API expects comma-separated tag IDs
            params["tagIds"] = ",".join(tag_ids)
        if start_date_from:
            params["startDateFrom"] = start_date_from
        if start_date_to:
            params["startDateTo"] = start_date_to
        if max_count:
            params["maxCount"] = str(max_count)

        logger.debug(f"Request params: {params}")
        result = await self._request("GET", "/task", params=params)

        # API returns {"tasks": [...]} format
        if isinstance(result, dict) and 'tasks' in result:
            tasks = result['tasks']
            logger.info(f"Found {len(tasks)} tasks")
            return tasks
        elif isinstance(result, list):
            # Fallback: if API returns list directly
            logger.info(f"Found {len(result)} tasks")
            return result
        else:
            logger.warning(f"Unexpected response format: {type(result)}")
            return []
    
    async def get_task(self, task_id: str) -> dict:
        """Get task by ID"""
        result = await self._request("GET", f"/task/{task_id}")
        return result if isinstance(result, dict) else {}
    
    async def create_task(
        self,
        title: str,
        start: str | None = None,
        note: str | None = None,
        priority: int = 1,
        project_id: str | None = None,
        parent: str | None = None,
    ) -> dict:
        """Create a new task

        Args:
            title: Task title (required)
            start: Start date in ISO 8601 format (e.g., 2024-01-01T00:00:00)
            note: Task description
            priority: 0=high, 1=normal, 2=low
            project_id: Project ID to add task to
            parent: Parent task ID for subtasks
        """
        # Log input parameters
        logger.info(f"Creating task with title='{title}', project_id='{project_id}', "
                   f"start='{start}', priority={priority}, parent='{parent}'")

        data: dict[str, Any] = {"title": title, "priority": priority}
        if start:
            data["start"] = start
        if note:
            data["note"] = note

        # Validate and add project_id
        if project_id and project_id.strip():  # Check for non-empty string
            # Validate format (should be P-XXX)
            if not project_id.startswith("P-"):
                logger.warning(f"Invalid project_id format: '{project_id}'. Expected format: P-XXX")
            else:
                logger.info(f"Adding project_id '{project_id}' to request")
                # Singularity API might require projectId field
                data["projectId"] = project_id
        else:
            if project_id == "":
                logger.warning("project_id is empty string, task will be created without project")
            else:
                logger.warning("No project_id provided, task will be created without project")

        if parent:
            data["parent"] = parent

        # Log final request data
        logger.debug(f"Final request data: {data}")

        result = await self._request("POST", "/task", json=data)
        logger.info(f"Task created successfully: {result.get('id', 'unknown ID')}")
        return result if isinstance(result, dict) else {}
    
    async def update_task(
        self,
        task_id: str,
        title: str | None = None,
        start: str | None = None,
        note: str | None = None,
        priority: int | None = None,
        project_id: str | None = None,
    ) -> dict:
        """Update an existing task"""
        data: dict[str, Any] = {}
        if title is not None:
            data["title"] = title
        if start is not None:
            data["start"] = start
        if note is not None:
            data["note"] = note
        if priority is not None:
            data["priority"] = priority
        if project_id is not None:
            # Singularity API requires both projectId and group for project assignment
            data["projectId"] = project_id
            # Generate group ID from project ID (Q- prefix + project ID suffix)
            # This is a simplification - in reality, group IDs might be different
            # but for now we'll use projectId field
            # The actual group should be fetched from project data
            # For P-6868b846-5c1d-49ee-8ab9-2376f8800968 -> Q-e7bb241d-b6c8-4907-b388-15dfb6bee33b
            # This needs to be resolved per-project
            logger.warning(f"Setting project {project_id} - group ID might need manual adjustment")

        result = await self._request("PATCH", f"/task/{task_id}", json=data)
        return result if isinstance(result, dict) else {}
    
    async def complete_task(self, task_id: str) -> dict:
        """Mark task as completed (archive it)"""
        from datetime import date
        data = {"journalDate": date.today().isoformat()}
        result = await self._request("PATCH", f"/task/{task_id}", json=data)
        return result if isinstance(result, dict) else {}
    
    async def delete_task(self, task_id: str) -> None:
        """Delete a task permanently"""
        await self._request("DELETE", f"/task/{task_id}")

    async def set_task_tags(
        self,
        task_id: str,
        tag_ids: list[str],
    ) -> dict:
        """Set tags for a task (replaces all existing tags)"""
        data = {"tags": tag_ids}
        result = await self._request("PATCH", f"/task/{task_id}", json=data)
        return result if isinstance(result, dict) else {}

    async def add_task_tag(
        self,
        task_id: str,
        tag_id: str,
    ) -> dict:
        """Add a tag to a task"""
        # First get current tags
        task = await self.get_task(task_id)
        current_tags = task.get("tags", [])

        # Add new tag if not already present
        if tag_id not in current_tags:
            current_tags.append(tag_id)
            return await self.set_task_tags(task_id, current_tags)

        return task

    async def remove_task_tag(
        self,
        task_id: str,
        tag_id: str,
    ) -> dict:
        """Remove a tag from a task"""
        # First get current tags
        task = await self.get_task(task_id)
        current_tags = task.get("tags", [])

        # Remove tag if present
        if tag_id in current_tags:
            current_tags.remove(tag_id)
            return await self.set_task_tags(task_id, current_tags)

        return task
    
    # ============ PROJECTS ============
    
    async def list_projects(
        self,
        include_archived: bool = False,
        include_removed: bool = False,
        max_count: int | None = 100,
    ) -> list[dict]:
        """Get list of projects"""
        params = {
            "includeArchived": str(include_archived).lower(),
            "includeRemoved": str(include_removed).lower(),
        }
        if max_count:
            params["maxCount"] = str(max_count)

        result = await self._request("GET", "/project", params=params)

        # API returns {"projects": [...]} format
        if isinstance(result, dict) and 'projects' in result:
            projects = result['projects']
            logger.info(f"Found {len(projects)} projects")
            return projects
        elif isinstance(result, list):
            # Fallback: if API returns list directly
            logger.info(f"Found {len(result)} projects")
            return result
        else:
            logger.warning(f"Unexpected projects response format: {type(result)}")
            return []
    
    async def get_project(self, project_id: str) -> dict:
        """Get project by ID"""
        result = await self._request("GET", f"/project/{project_id}")
        return result if isinstance(result, dict) else {}
    
    async def create_project(
        self,
        title: str,
        note: str | None = None,
        color: str | None = None,
        emoji: str | None = None,
    ) -> dict:
        """Create a new project
        
        Args:
            title: Project title (required)
            note: Project description
            color: HEX color (e.g. "#ad1457")
            emoji: Emoji hex code (e.g. "1f49e")
        """
        data: dict[str, Any] = {"title": title}
        if note:
            data["note"] = note
        if color:
            data["color"] = color
        if emoji:
            data["emoji"] = emoji
        
        result = await self._request("POST", "/project", json=data)
        return result if isinstance(result, dict) else {}
    
    async def update_project(
        self,
        project_id: str,
        title: str | None = None,
        note: str | None = None,
        color: str | None = None,
    ) -> dict:
        """Update an existing project"""
        data: dict[str, Any] = {}
        if title is not None:
            data["title"] = title
        if note is not None:
            data["note"] = note
        if color is not None:
            data["color"] = color
        
        result = await self._request("PATCH", f"/project/{project_id}", json=data)
        return result if isinstance(result, dict) else {}
    
    async def delete_project(self, project_id: str) -> None:
        """Delete a project permanently"""
        await self._request("DELETE", f"/project/{project_id}")
    
    # ============ HABITS ============
    
    async def list_habits(self, max_count: int | None = 100) -> list[dict]:
        """Get list of habits"""
        params = {}
        if max_count:
            params["maxCount"] = str(max_count)
        
        result = await self._request("GET", "/habit", params=params)
        return result if isinstance(result, list) else []
    
    async def create_habit(
        self,
        title: str,
        description: str | None = None,
        color: str | None = None,
    ) -> dict:
        """Create a new habit
        
        Args:
            title: Habit title (required)
            description: Habit description
            color: Color name (e.g. "red", "blue", "green")
        """
        data: dict[str, Any] = {"title": title}
        if description:
            data["description"] = description
        if color:
            data["color"] = color
        
        result = await self._request("POST", "/habit", json=data)
        return result if isinstance(result, dict) else {}
    
    async def mark_habit(
        self,
        habit_id: str,
        date: str,
        progress: int = 2,
    ) -> dict:
        """Mark habit progress

        Args:
            habit_id: Habit ID
            date: Date in ISO 8601 format (e.g., 2024-01-01T00:00:00)
            progress: 0=no change, 1=not done (keeps streak), 2=done
        """
        data = {
            "habit": habit_id,
            "date": date,
            "progress": progress,
        }
        result = await self._request("POST", "/habit-progress", json=data)
        return result if isinstance(result, dict) else {}
    
    async def delete_habit(self, habit_id: str) -> None:
        """Delete a habit"""
        await self._request("DELETE", f"/habit/{habit_id}")
    
    # ============ TAGS ============
    
    async def list_tags(
        self,
        include_removed: bool = False,
        max_count: int | None = 100,
    ) -> list[dict]:
        """Get list of tags"""
        params = {
            "includeRemoved": str(include_removed).lower(),
        }
        if max_count:
            params["maxCount"] = str(max_count)

        result = await self._request("GET", "/tag", params=params)

        # API might return {"tags": [...]} format
        if isinstance(result, dict) and 'tags' in result:
            return result['tags']
        elif isinstance(result, list):
            return result
        else:
            logger.warning(f"Unexpected tags response format: {type(result)}")
            return []
    
    async def create_tag(
        self,
        title: str,
        parent: str | None = None,
    ) -> dict:
        """Create a new tag"""
        data: dict[str, Any] = {"title": title}
        if parent:
            data["parent"] = parent
        
        result = await self._request("POST", "/tag", json=data)
        return result if isinstance(result, dict) else {}
    
    async def get_tag(self, tag_id: str) -> dict:
        """Get tag by ID"""
        result = await self._request("GET", f"/tag/{tag_id}")
        return result if isinstance(result, dict) else {}

    async def update_tag(
        self,
        tag_id: str,
        title: str | None = None,
    ) -> dict:
        """Update an existing tag"""
        data: dict[str, Any] = {}
        if title is not None:
            data["title"] = title

        result = await self._request("PATCH", f"/tag/{tag_id}", json=data)
        return result if isinstance(result, dict) else {}

    async def delete_tag(self, tag_id: str) -> None:
        """Delete a tag"""
        await self._request("DELETE", f"/tag/{tag_id}")
    
    # ============ CHECKLIST ============
    
    async def create_checklist_item(
        self,
        task_id: str,
        title: str,
    ) -> dict:
        """Add checklist item to a task"""
        data = {
            "title": title,
            "parent": task_id,
        }
        result = await self._request("POST", "/checklist-item", json=data)
        return result if isinstance(result, dict) else {}
