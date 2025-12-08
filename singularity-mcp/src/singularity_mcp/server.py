"""
SingularityApp MCP Server

MCP server for integrating SingularityApp task manager with Claude Code.
"""

import os
import json
import asyncio
import logging
from datetime import date

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

from .api import SingularityAPI

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


# Initialize server
server = Server("singularity-mcp")

# API client (initialized on first use)
_api: SingularityAPI | None = None


def get_api() -> SingularityAPI:
    """Get or create API client"""
    global _api
    if _api is None:
        token = os.environ.get("SINGULARITY_API_TOKEN")
        if not token:
            raise ValueError(
                "SINGULARITY_API_TOKEN environment variable is required. "
                "Get your token at https://me.singularity-app.com"
            )
        _api = SingularityAPI(token)
    return _api


# ============ TOOL DEFINITIONS ============

TOOLS = [
    # Tasks
    Tool(
        name="list_tasks",
        description="Get list of tasks from SingularityApp. Can filter by project, date range, etc.",
        inputSchema={
            "type": "object",
            "properties": {
                "project_id": {
                    "type": "string",
                    "description": "Filter by project ID",
                },
                "start_date_from": {
                    "type": "string",
                    "description": "Filter tasks starting from this date (ISO 8601 format, e.g., 2024-01-01T00:00:00)",
                },
                "start_date_to": {
                    "type": "string",
                    "description": "Filter tasks up to this date (ISO 8601 format, e.g., 2024-01-01T23:59:59)",
                },
                "include_archived": {
                    "type": "boolean",
                    "description": "Include archived tasks",
                    "default": False,
                },
                "max_count": {
                    "type": "integer",
                    "description": "Maximum number of tasks to return",
                    "default": 100,
                },
            },
        },
    ),
    Tool(
        name="get_task",
        description="Get a specific task by ID",
        inputSchema={
            "type": "object",
            "properties": {
                "task_id": {
                    "type": "string",
                    "description": "Task ID (e.g., T-123)",
                },
            },
            "required": ["task_id"],
        },
    ),
    Tool(
        name="create_task",
        description="Create a new task in SingularityApp",
        inputSchema={
            "type": "object",
            "properties": {
                "title": {
                    "type": "string",
                    "description": "Task title",
                },
                "start": {
                    "type": "string",
                    "description": "Start date (ISO 8601 format, e.g., 2024-01-01T00:00:00). If not specified, task goes to Inbox.",
                },
                "note": {
                    "type": "string",
                    "description": "Task description/notes",
                },
                "priority": {
                    "type": "integer",
                    "description": "Priority: 0=high, 1=normal, 2=low",
                    "default": 1,
                },
                "project_id": {
                    "type": "string",
                    "description": "Project ID to add task to",
                },
                "parent": {
                    "type": "string",
                    "description": "Parent task ID (for creating subtasks)",
                },
            },
            "required": ["title"],
        },
    ),
    Tool(
        name="update_task",
        description="Update an existing task",
        inputSchema={
            "type": "object",
            "properties": {
                "task_id": {
                    "type": "string",
                    "description": "Task ID to update",
                },
                "title": {
                    "type": "string",
                    "description": "New task title",
                },
                "start": {
                    "type": "string",
                    "description": "New start date (ISO 8601 format, e.g., 2024-01-01T00:00:00)",
                },
                "note": {
                    "type": "string",
                    "description": "New task description",
                },
                "priority": {
                    "type": "integer",
                    "description": "New priority: 0=high, 1=normal, 2=low",
                },
            },
            "required": ["task_id"],
        },
    ),
    Tool(
        name="complete_task",
        description="Mark a task as completed",
        inputSchema={
            "type": "object",
            "properties": {
                "task_id": {
                    "type": "string",
                    "description": "Task ID to complete",
                },
            },
            "required": ["task_id"],
        },
    ),
    Tool(
        name="delete_task",
        description="Delete a task permanently",
        inputSchema={
            "type": "object",
            "properties": {
                "task_id": {
                    "type": "string",
                    "description": "Task ID to delete",
                },
            },
            "required": ["task_id"],
        },
    ),
    
    # Projects
    Tool(
        name="list_projects",
        description="Get list of all projects",
        inputSchema={
            "type": "object",
            "properties": {
                "include_archived": {
                    "type": "boolean",
                    "description": "Include archived projects",
                    "default": False,
                },
                "max_count": {
                    "type": "integer",
                    "description": "Maximum number of projects to return",
                    "default": 100,
                },
            },
        },
    ),
    Tool(
        name="create_project",
        description="Create a new project",
        inputSchema={
            "type": "object",
            "properties": {
                "title": {
                    "type": "string",
                    "description": "Project title",
                },
                "note": {
                    "type": "string",
                    "description": "Project description",
                },
                "color": {
                    "type": "string",
                    "description": "Project color in HEX format (e.g., #ad1457)",
                },
            },
            "required": ["title"],
        },
    ),
    Tool(
        name="delete_project",
        description="Delete a project permanently",
        inputSchema={
            "type": "object",
            "properties": {
                "project_id": {
                    "type": "string",
                    "description": "Project ID to delete",
                },
            },
            "required": ["project_id"],
        },
    ),
    
    # Habits
    Tool(
        name="list_habits",
        description="Get list of all habits",
        inputSchema={
            "type": "object",
            "properties": {
                "max_count": {
                    "type": "integer",
                    "description": "Maximum number of habits to return",
                    "default": 100,
                },
            },
        },
    ),
    Tool(
        name="create_habit",
        description="Create a new habit",
        inputSchema={
            "type": "object",
            "properties": {
                "title": {
                    "type": "string",
                    "description": "Habit title",
                },
                "description": {
                    "type": "string",
                    "description": "Habit description",
                },
                "color": {
                    "type": "string",
                    "description": "Color name (red, pink, purple, blue, green, etc.)",
                },
            },
            "required": ["title"],
        },
    ),
    Tool(
        name="mark_habit",
        description="Mark a habit as done for a specific date",
        inputSchema={
            "type": "object",
            "properties": {
                "habit_id": {
                    "type": "string",
                    "description": "Habit ID",
                },
                "date": {
                    "type": "string",
                    "description": "Date (ISO 8601 format, e.g., 2024-01-01T00:00:00). Defaults to today.",
                },
                "done": {
                    "type": "boolean",
                    "description": "True=done, False=not done (keeps streak)",
                    "default": True,
                },
            },
            "required": ["habit_id"],
        },
    ),
    
    # Tags
    Tool(
        name="list_tags",
        description="Get list of all tags",
        inputSchema={
            "type": "object",
            "properties": {
                "max_count": {
                    "type": "integer",
                    "description": "Maximum number of tags to return",
                    "default": 100,
                },
            },
        },
    ),
    Tool(
        name="create_tag",
        description="Create a new tag",
        inputSchema={
            "type": "object",
            "properties": {
                "title": {
                    "type": "string",
                    "description": "Tag title",
                },
                "parent": {
                    "type": "string",
                    "description": "Parent tag ID for nested tags",
                },
            },
            "required": ["title"],
        },
    ),
    
    # Checklist
    Tool(
        name="add_checklist_item",
        description="Add a checklist item to a task",
        inputSchema={
            "type": "object",
            "properties": {
                "task_id": {
                    "type": "string",
                    "description": "Task ID to add checklist item to",
                },
                "title": {
                    "type": "string",
                    "description": "Checklist item text",
                },
            },
            "required": ["task_id", "title"],
        },
    ),
    
    # Utility
    Tool(
        name="get_today_tasks",
        description="Get all tasks scheduled for today",
        inputSchema={
            "type": "object",
            "properties": {},
        },
    ),
]


@server.list_tools()
async def list_tools() -> list[Tool]:
    """Return list of available tools"""
    return TOOLS


@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    """Handle tool calls"""
    logger.info(f"Tool called: {name}")
    logger.debug(f"Arguments received: {arguments}")

    api = get_api()

    try:
        result = await _execute_tool(api, name, arguments)
        logger.info(f"Tool {name} executed successfully")
        return [TextContent(type="text", text=json.dumps(result, ensure_ascii=False, indent=2))]
    except Exception as e:
        logger.error(f"Error executing tool {name}: {str(e)}", exc_info=True)
        return [TextContent(type="text", text=f"Error: {str(e)}")]


async def _execute_tool(api: SingularityAPI, name: str, args: dict):
    """Execute a tool and return result"""
    
    # Tasks
    if name == "list_tasks":
        return await api.list_tasks(
            project_id=args.get("project_id"),
            include_archived=args.get("include_archived", False),
            start_date_from=args.get("start_date_from"),
            start_date_to=args.get("start_date_to"),
            max_count=args.get("max_count", 100),
        )
    
    elif name == "get_task":
        return await api.get_task(args["task_id"])
    
    elif name == "create_task":
        logger.info(f"Executing create_task with args: {args}")

        # Extract and log project_id specifically
        project_id = args.get("project_id")
        logger.info(f"project_id value: '{project_id}' (type: {type(project_id).__name__})")

        # Check if project_id is empty string
        if project_id == "":
            logger.warning("project_id is empty string, will be treated as None")
            project_id = None

        return await api.create_task(
            title=args["title"],
            start=args.get("start"),
            note=args.get("note"),
            priority=args.get("priority", 1),
            project_id=project_id,
            parent=args.get("parent"),
        )
    
    elif name == "update_task":
        return await api.update_task(
            task_id=args["task_id"],
            title=args.get("title"),
            start=args.get("start"),
            note=args.get("note"),
            priority=args.get("priority"),
        )
    
    elif name == "complete_task":
        return await api.complete_task(args["task_id"])
    
    elif name == "delete_task":
        await api.delete_task(args["task_id"])
        return {"status": "deleted", "task_id": args["task_id"]}
    
    # Projects
    elif name == "list_projects":
        return await api.list_projects(
            include_archived=args.get("include_archived", False),
            max_count=args.get("max_count", 100),
        )
    
    elif name == "create_project":
        return await api.create_project(
            title=args["title"],
            note=args.get("note"),
            color=args.get("color"),
        )
    
    elif name == "delete_project":
        await api.delete_project(args["project_id"])
        return {"status": "deleted", "project_id": args["project_id"]}
    
    # Habits
    elif name == "list_habits":
        return await api.list_habits(max_count=args.get("max_count", 100))
    
    elif name == "create_habit":
        return await api.create_habit(
            title=args["title"],
            description=args.get("description"),
            color=args.get("color"),
        )
    
    elif name == "mark_habit":
        from datetime import datetime
        habit_date = args.get("date")
        if not habit_date:
            habit_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0).isoformat()
        progress = 2 if args.get("done", True) else 1
        return await api.mark_habit(
            habit_id=args["habit_id"],
            date=habit_date,
            progress=progress,
        )
    
    # Tags
    elif name == "list_tags":
        return await api.list_tags(max_count=args.get("max_count", 100))
    
    elif name == "create_tag":
        return await api.create_tag(
            title=args["title"],
            parent=args.get("parent"),
        )
    
    # Checklist
    elif name == "add_checklist_item":
        return await api.create_checklist_item(
            task_id=args["task_id"],
            title=args["title"],
        )
    
    # Utility
    elif name == "get_today_tasks":
        from datetime import date
        # Use date only format (YYYY-MM-DD) as per API documentation
        today = date.today().isoformat()  # Returns YYYY-MM-DD
        logger.info(f"Getting tasks for today: {today}")
        return await api.list_tasks(
            start_date_from=today,
            start_date_to=today,
        )
    
    else:
        raise ValueError(f"Unknown tool: {name}")


def main():
    """Main entry point"""
    async def run():
        async with stdio_server() as (read_stream, write_stream):
            await server.run(
                read_stream,
                write_stream,
                server.create_initialization_options(),
            )
    
    asyncio.run(run())


if __name__ == "__main__":
    main()
