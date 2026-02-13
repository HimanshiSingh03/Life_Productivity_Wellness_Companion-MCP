from __future__ import annotations
from datetime import datetime, date, timedelta
from typing import List, Dict, TypedDict, Optional
from fastmcp import FastMCP

# ==========================================
# MCP INIT
# ==========================================
mcp = FastMCP("Life_Productivity_Wellness_Companion_Pro")

# ==========================================
# DATA MODELS
# ==========================================

class Task(TypedDict):
    ID: int
    Title: str
    Category: str
    Priority: str
    DurationHours: float
    CreatedAt: str
    DueDate: Optional[str]
    Status: str
    XP: int


class ProductivityReport(TypedDict):
    TotalTasks: int
    CompletedTasks: int
    CompletionRate: float
    TotalXP: int
    Level: str


class BurnoutReport(TypedDict):
    PendingHours: float
    BurnoutRisk: str
    Suggestion: str


# ==========================================
# IN-MEMORY STORAGE
# ==========================================

tasks: List[Task] = []
water_logs: Dict[str, float] = {}
mood_logs: Dict[str, str] = {}
task_id_counter: int = 1


# ==========================================
# LEVEL SYSTEM
# ==========================================

def calculate_level(total_xp: int) -> str:
    if total_xp >= 500:
        return "Elite Performer"
    elif total_xp >= 300:
        return "Advanced Achiever"
    elif total_xp >= 150:
        return "Consistent Performer"
    elif total_xp >= 50:
        return "Rising Star"
    return "Beginner"


# ==========================================
# ➕ ADD TASK (SMART XP SYSTEM)
# ==========================================
@mcp.tool()
def add_task(
    title: str,
    duration_hours: float,
    category: str = "Study",
    priority: str = "Medium",
    due_date: Optional[str] = None,
) -> Dict[str, str | int]:

    global task_id_counter

    created_at: str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    priority_bonus: int = 10 if priority.lower() == "high" else 5
    category_bonus: int = 5 if category.lower() == "exercise" else 0
    xp: int = int(duration_hours * 20 + priority_bonus + category_bonus)

    task: Task = {
        "ID": task_id_counter,
        "Title": title,
        "Category": category,
        "Priority": priority,
        "DurationHours": duration_hours,
        "CreatedAt": created_at,
        "DueDate": due_date,
        "Status": "Pending",
        "XP": xp,
    }

    tasks.append(task)
    task_id_counter += 1

    return {
        "Message": "Task added successfully",
        "XPAssigned": xp,
    }


# ==========================================
# 📋 LIST TASKS
# ==========================================
@mcp.tool()
def list_tasks() -> List[Task]:
    return tasks


# ==========================================
# ✅ COMPLETE TASK
# ==========================================
@mcp.tool()
def complete_task(task_id: int) -> Dict[str, str | int]:

    for task in tasks:
        if task["ID"] == task_id:
            if task["Status"] == "Completed":
                return {"Message": "Task already completed"}

            task["Status"] = "Completed"
            return {
                "Message": "Task completed",
                "XPEarned": task["XP"],
            }

    return {"Message": "Task not found"}


# ==========================================
# 📊 PRODUCTIVITY ANALYTICS
# ==========================================
@mcp.tool()
def productivity_report() -> ProductivityReport:

    completed = [t for t in tasks if t["Status"] == "Completed"]
    total_xp = sum(t["XP"] for t in completed)

    completion_rate = (
        (len(completed) / len(tasks)) * 100
        if tasks else 0
    )

    return {
        "TotalTasks": len(tasks),
        "CompletedTasks": len(completed),
        "CompletionRate": round(completion_rate, 2),
        "TotalXP": total_xp,
        "Level": calculate_level(total_xp),
    }


# ==========================================
# 🔥 SMART BURNOUT DETECTION
# ==========================================
@mcp.tool()
def burnout_analysis() -> BurnoutReport:

    pending_hours = sum(
        t["DurationHours"]
        for t in tasks
        if t["Status"] == "Pending"
    )

    if pending_hours >= 8:
        return {
            "PendingHours": pending_hours,
            "BurnoutRisk": "High",
            "Suggestion": "Reduce workload and take proper breaks",
        }
    elif pending_hours >= 4:
        return {
            "PendingHours": pending_hours,
            "BurnoutRisk": "Moderate",
            "Suggestion": "Schedule short breaks every 45 minutes",
        }

    return {
        "PendingHours": pending_hours,
        "BurnoutRisk": "Low",
        "Suggestion": "Workload balanced",
    }


# ==========================================
# 💧 HYDRATION SYSTEM
# ==========================================
@mcp.tool()
def log_water(amount_liters: float) -> Dict[str, str | float]:

    today = str(date.today())

    if today not in water_logs:
        water_logs[today] = 0.0

    water_logs[today] += amount_liters
    total = water_logs[today]

    return {
        "Date": today,
        "TotalWater": total,
        "Status": "Excellent" if total >= 2.5 else "Drink more water",
    }


# ==========================================
# 😊 MOOD TRACKER
# ==========================================
@mcp.tool()
def log_mood(mood: str) -> Dict[str, str]:

    today = str(date.today())
    mood_logs[today] = mood

    return {
        "Date": today,
        "MoodLogged": mood,
    }


# ==========================================
# 🧠 SMART TASK ORDERING
# ==========================================
@mcp.tool()
def smart_task_order() -> List[Task]:

    return sorted(
        tasks,
        key=lambda x: (x["Priority"], -x["DurationHours"]),
        reverse=True,
    )


# ==========================================
# 📝 ADVANCED NOTES GENERATOR
# ==========================================
@mcp.tool()
def generate_notes(topic: str) -> Dict[str, List[str] | str]:

    return {
        "Topic": topic,
        "DeepConcepts": [
            f"Core theory of {topic}",
            "Advanced implementation details",
            "Optimization strategies",
        ],
        "RealWorldApplications": [
            "Industry use cases",
            "Case study examples",
        ],
        "CommonPitfalls": [
            "Frequent mistakes",
            "Debugging strategies",
        ],
        "InterviewQuestions": [
            f"What is {topic}?",
            f"Explain advantages of {topic}",
        ],
        "RevisionChecklist": [
            "Understand fundamentals",
            "Practice examples",
            "Solve real-world problems",
        ],
    }


# ==========================================
# 🚀 RUN SERVER
# ==========================================
if __name__ == "__main__":
    mcp.run(transport="http", host="0.0.0.0", port=8000)