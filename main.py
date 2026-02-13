from datetime import datetime, date, timedelta
from typing import List, Dict
from fastmcp import FastMCP

mcp = FastMCP("Life_Productivity_Wellness_Companion_Pro")

# In-memory storage
tasks: List[Dict[str, str]] = []
task_id_counter: int = 1


# ==========================================
# ADD TASK
# ==========================================
@mcp.tool()
def add_task(
    title: str,
    duration_hours: float,
    category: str,
    priority: str,
    due_date: str
) -> Dict[str, str]:
    """
    Add a new task.
    """

    global task_id_counter

    created_at = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

    points = int(duration_hours * 10)
    if priority.lower() == "high":
        points += 10

    task = {
        "ID": str(task_id_counter),
        "Title": title,
        "Category": category,
        "Priority": priority,
        "DurationHours": str(duration_hours),
        "CreatedAt": created_at,
        "DueDate": due_date,
        "Status": "Pending",
        "Points": str(points),
    }

    tasks.append(task)
    task_id_counter += 1

    return {
        "Message": "Task Added Successfully",
        "PointsAssigned": str(points)
    }


# ==========================================
# COMPLETE TASK
# ==========================================
@mcp.tool()
def complete_task(task_id: int) -> Dict[str, str]:
    """
    Mark a task as completed.
    """

    for task in tasks:
        if int(task["ID"]) == task_id:
            task["Status"] = "Completed"
            return {
                "Message": "Task Completed",
                "PointsEarned": task["Points"]
            }

    return {
        "Message": "Task Not Found",
        "PointsEarned": "0"
    }


# ==========================================
# LIST TASKS
# ==========================================
@mcp.tool()
def list_tasks() -> List[Dict[str, str]]:
    """
    Return all tasks.
    """
    return tasks


# ==========================================
# TOTAL POINTS
# ==========================================
@mcp.tool()
def total_points() -> Dict[str, str]:
    """
    Calculate total earned points.
    """

    total = sum(
        int(task["Points"])
        for task in tasks
        if task["Status"] == "Completed"
    )

    return {
        "TotalPoints": str(total)
    }


# ==========================================
# RUN SERVER
# ==========================================
if __name__ == "__main__":
    mcp.run(transport="http", host="0.0.0.0", port=8000)