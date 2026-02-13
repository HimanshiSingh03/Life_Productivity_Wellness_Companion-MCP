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
    Points: int


class MoodLog(TypedDict):
    Date: str
    MoodScore: int
    Note: str


class SleepLog(TypedDict):
    Date: str
    SleepHours: float


class Goal(TypedDict):
    Title: str
    TargetHours: float
    CompletedHours: float
    ProgressPercent: float


# ==========================================
# IN-MEMORY STORAGE
# ==========================================

tasks: List[Task] = []
mood_logs: List[MoodLog] = []
sleep_logs: List[SleepLog] = []
goals: List[Goal] = []
water_logs: Dict[str, float] = {}

task_id_counter: int = 1


# ==========================================
# TASK MANAGEMENT
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

    created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    bonus = 10 if priority.lower() == "high" else 0
    points = int(duration_hours * 15 + bonus)

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
        "Message": "Task Added Successfully",
        "PointsAssigned": points,
    }


@mcp.tool()
def complete_task(task_id: int) -> Dict[str, str | int]:

    for task in tasks:
        if task["ID"] == task_id:

            if task["Status"] == "Completed":
                return {"Message": "Task already completed"}

            task["Status"] = "Completed"

            return {
                "Message": "Task Completed",
                "PointsEarned": task["Points"],
            }

    return {"Message": "Task not found"}


@mcp.tool()
def list_tasks() -> List[Task]:
    return tasks


# ==========================================
# GOAL TRACKING
# ==========================================

@mcp.tool()
def set_goal(title: str, target_hours: float) -> Goal:

    goal: Goal = {
        "Title": title,
        "TargetHours": target_hours,
        "CompletedHours": 0.0,
        "ProgressPercent": 0.0,
    }

    goals.append(goal)
    return goal


@mcp.tool()
def update_goal_progress(title: str) -> Goal:

    for goal in goals:
        if goal["Title"] == title:

            completed = sum(
                t["DurationHours"]
                for t in tasks
                if t["Status"] == "Completed"
            )

            goal["CompletedHours"] = completed
            goal["ProgressPercent"] = round(
                (completed / goal["TargetHours"]) * 100, 2
            )

            return goal

    return {"Title": "Goal not found", "TargetHours": 0, "CompletedHours": 0, "ProgressPercent": 0}


# ==========================================
# MOOD & SLEEP TRACKING
# ==========================================

@mcp.tool()
def log_mood(score: int, note: str = "") -> MoodLog:

    entry: MoodLog = {
        "Date": str(date.today()),
        "MoodScore": score,
        "Note": note,
    }

    mood_logs.append(entry)
    return entry


@mcp.tool()
def log_sleep(hours: float) -> SleepLog:

    entry: SleepLog = {
        "Date": str(date.today()),
        "SleepHours": hours,
    }

    sleep_logs.append(entry)
    return entry


# ==========================================
# HYDRATION
# ==========================================

@mcp.tool()
def log_water(amount_liters: float) -> Dict[str, str | float]:

    today = str(date.today())

    if today not in water_logs:
        water_logs[today] = 0.0

    water_logs[today] += amount_liters

    total = water_logs[today]

    status = "Excellent Hydration" if total >= 2.5 else "Drink More Water"

    return {
        "Date": today,
        "TotalWaterLiters": total,
        "Status": status,
    }


# ==========================================
# ANALYTICS
# ==========================================

@mcp.tool()
def weekly_productivity() -> Dict[str, float]:

    last_7_days = date.today() - timedelta(days=7)

    completed = [
        t for t in tasks
        if t["Status"] == "Completed"
        and datetime.strptime(t["CreatedAt"][:10], "%Y-%m-%d").date() >= last_7_days
    ]

    total_hours = sum(t["DurationHours"] for t in completed)

    return {
        "CompletedTasksLast7Days": len(completed),
        "TotalStudyHoursLast7Days": total_hours,
    }


@mcp.tool()
def burnout_risk() -> Dict[str, str | float]:

    pending_hours = sum(
        t["DurationHours"]
        for t in tasks
        if t["Status"] == "Pending"
    )

    avg_sleep = (
        sum(s["SleepHours"] for s in sleep_logs) / len(sleep_logs)
        if sleep_logs else 0
    )

    avg_mood = (
        sum(m["MoodScore"] for m in mood_logs) / len(mood_logs)
        if mood_logs else 0
    )

    burnout_score = pending_hours * 2 - avg_sleep * 1.5 - avg_mood

    risk = "High Risk" if burnout_score > 10 else "Moderate" if burnout_score > 5 else "Low"

    return {
        "BurnoutScore": round(burnout_score, 2),
        "RiskLevel": risk,
    }


# ==========================================
# STREAK
# ==========================================

@mcp.tool()
def streak() -> Dict[str, int]:

    completed_days = sorted(
        {
            t["CreatedAt"][:10]
            for t in tasks
            if t["Status"] == "Completed"
        },
        reverse=True,
    )

    streak_count = 0
    today = date.today()

    for i, day_str in enumerate(completed_days):
        day_date = datetime.strptime(day_str, "%Y-%m-%d").date()
        if day_date == today - timedelta(days=i):
            streak_count += 1
        else:
            break

    return {"CurrentStreakDays": streak_count}


# ==========================================
# SMART SUGGESTION ENGINE
# ==========================================

@mcp.tool()
def smart_suggestion() -> Dict[str, str]:

    burnout = burnout_risk()["RiskLevel"]

    if burnout == "High Risk":
        return {"Suggestion": "Reduce workload and take recovery break"}
    if burnout == "Moderate":
        return {"Suggestion": "Balance study with light exercise"}
    return {"Suggestion": "You're performing well. Keep going!"}


# ==========================================
# CLEAR ALL DATA
# ==========================================

@mcp.tool()
def reset_system() -> Dict[str, str]:

    global tasks, mood_logs, sleep_logs, goals, water_logs, task_id_counter

    tasks = []
    mood_logs = []
    sleep_logs = []
    goals = []
    water_logs = {}
    task_id_counter = 1

    return {"Message": "System Reset Successfully"}


# ==========================================
# RUN SERVER
# ==========================================

if __name__ == "__main__":
    mcp.run(transport="http", host="0.0.0.0", port=8000)