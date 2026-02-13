from __future__ import annotations
from datetime import datetime, date, timedelta
from typing import List, Dict, TypedDict, Optional
from fastmcp import FastMCP

# =====================================
# MCP INIT
# =====================================
mcp = FastMCP("Life_Productivity_Wellness_Companion")


# =====================================
# DATA MODELS (STRICT TYPES)
# =====================================

class Task(TypedDict):
    ID: int
    Title: str
    Category: str
    Priority: str
    DurationHours: float
    CreatedAt: str
    DueDate: Optional[str]
    Status: str
    Points: int


class Summary(TypedDict):
    TotalTasks: int
    CompletedTasks: int
    PendingTasks: int
    TotalPointsEarned: int


class HydrationLog(TypedDict):
    Date: str
    TotalWaterLiters: float
    HydrationStatus: str


class StreakResult(TypedDict):
    CurrentStreakDays: int


class AchievementResult(TypedDict):
    CurrentPoints: int
    CurrentStreak: int
    UnlockedBadges: List[str]


# =====================================
# IN-MEMORY STORAGE
# =====================================

tasks: List[Task] = []
water_logs: Dict[str, float] = {}
task_id_counter: int = 1


# =====================================
# ➕ ADD TASK
# =====================================
@mcp.tool()
def add_task(
    title: str,
    duration_hours: float,
    category: str = "Study",
    priority: str = "Medium",
    due_date: Optional[str] = None,
) -> Dict[str, int | str]:

    global task_id_counter

    created_at: str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    bonus: int = 5 if priority.lower() == "high" else 0
    points: int = int(duration_hours * 10 + bonus)

    task: Task = {
        "ID": task_id_counter,
        "Title": title,
        "Category": category,
        "Priority": priority,
        "DurationHours": duration_hours,
        "CreatedAt": created_at,
        "DueDate": due_date,
        "Status": "Pending",
        "Points": points,
    }

    tasks.append(task)
    task_id_counter += 1

    return {
        "Message": f"Task '{title}' added successfully",
        "PointsAssigned": points,
    }


# =====================================
# 📋 LIST TASKS
# =====================================
@mcp.tool()
def list_tasks() -> List[Task]:
    return tasks


# =====================================
# ✅ COMPLETE TASK
# =====================================
@mcp.tool()
def complete_task(task_id: int) -> Dict[str, int | str]:

    for task in tasks:
        if task["ID"] == task_id:
            if task["Status"] == "Completed":
                return {"Message": "Task already completed"}

            task["Status"] = "Completed"

            return {
                "Message": "Task completed successfully",
                "PointsEarned": task["Points"],
            }

    return {"Message": "Task not found"}


# =====================================
# ⏳ PENDING TASKS
# =====================================
@mcp.tool()
def pending_tasks() -> List[Task]:
    return [task for task in tasks if task["Status"] == "Pending"]


# =====================================
# 💰 TOTAL POINTS
# =====================================
@mcp.tool()
def total_points() -> Summary:

    completed: List[Task] = [
        task for task in tasks if task["Status"] == "Completed"
    ]

    total: int = sum(task["Points"] for task in completed)

    return {
        "TotalTasks": len(tasks),
        "CompletedTasks": len(completed),
        "PendingTasks": len(tasks) - len(completed),
        "TotalPointsEarned": total,
    }


# =====================================
# 🔥 STREAK
# =====================================
@mcp.tool()
def streak() -> StreakResult:

    completed_days: List[str] = sorted(
        list(
            {
                task["CreatedAt"][:10]
                for task in tasks
                if task["Status"] == "Completed"
            }
        ),
        reverse=True,
    )

    streak_count: int = 0
    today: date = date.today()

    for i, day_str in enumerate(completed_days):
        day_date: date = datetime.strptime(day_str, "%Y-%m-%d").date()
        if day_date == today - timedelta(days=i):
            streak_count += 1
        else:
            break

    return {"CurrentStreakDays": streak_count}


# =====================================
# 🏆 ACHIEVEMENTS
# =====================================
@mcp.tool()
def achievements() -> AchievementResult:

    summary: Summary = total_points()
    total: int = summary["TotalPointsEarned"]
    streak_days: int = streak()["CurrentStreakDays"]

    badges: List[str] = []

    if total >= 50:
        badges.append("Rookie Productivity")
    if total >= 100:
        badges.append("Pro Productivity")
    if streak_days >= 3:
        badges.append("3-Day Consistency")
    if streak_days >= 7:
        badges.append("7-Day Discipline Master")

    if not badges:
        badges.append("Keep progressing to unlock achievements")

    return {
        "CurrentPoints": total,
        "CurrentStreak": streak_days,
        "UnlockedBadges": badges,
    }


# =====================================
# 💧 LOG WATER
# =====================================
@mcp.tool()
def log_water(
    amount_liters: float,
    log_date: Optional[str] = None
) -> HydrationLog:

    if log_date is None:
        log_date = str(date.today())

    if log_date not in water_logs:
        water_logs[log_date] = 0.0

    water_logs[log_date] += amount_liters
    total: float = water_logs[log_date]

    status: str = (
        "Excellent hydration" if total >= 2.5 else "Drink more water"
    )

    return {
        "Date": log_date,
        "TotalWaterLiters": total,
        "HydrationStatus": status,
    }


# =====================================
# 💡 SUGGEST BREAKS
# =====================================
@mcp.tool()
def suggest_breaks() -> Dict[str, float | str]:

    total_hours: float = sum(
        task["DurationHours"]
        for task in tasks
        if task["Status"] == "Pending"
    )

    suggestion: str = (
        "Take a short 5–10 minute break"
        if total_hours >= 2
        else "Study load balanced"
    )

    return {
        "PendingStudyHours": total_hours,
        "Suggestion": suggestion,
    }


# =====================================
# 📝 GENERATE NOTES
# =====================================
@mcp.tool()
def generate_notes(topic: str) -> Dict[str, str | List[str]]:

    return {
        "Topic": topic,
        "Introduction": f"Overview of {topic}",
        "CoreConcepts": [
            "Key principles",
            "Important terminology",
            "Foundational rules",
        ],
        "Applications": [
            "Real-world use cases",
            "Implementation scenarios",
        ],
        "CommonMistakes": [
            "Conceptual misunderstandings",
            "Incorrect implementation patterns",
        ],
        "RevisionPoints": [
            "Quick recap",
            "Exam-focused highlights",
        ],
    }


# =====================================
# 🗑 CLEAR TASKS
# =====================================
@mcp.tool()
def clear_tasks() -> Dict[str, str]:

    global tasks, task_id_counter
    tasks = []
    task_id_counter = 1

    return {"Message": "All tasks cleared successfully"}


# =====================================
# 🚀 RUN SERVER
# =====================================
if __name__ == "__main__":
    mcp.run(transport="http", host="0.0.0.0", port=8000)