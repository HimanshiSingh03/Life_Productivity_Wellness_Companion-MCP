from datetime import datetime, date, timedelta
from fastmcp import FastMCP

# -----------------------------
# MCP INIT
# -----------------------------
mcp = FastMCP("Life_Productivity_Wellness_Companion")

# -----------------------------
# IN-MEMORY STORAGE
# -----------------------------
tasks = []
water_logs = {}
task_id_counter = 1

# -----------------------------
# ➕ Add Task
# -----------------------------
@mcp.tool()
def add_task(title: str,
             duration_hours: float,
             category: str = "Study",
             priority: str = "Medium",
             due_date: str = None) -> dict:

    global task_id_counter

    created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    bonus = 5 if priority.lower() == "high" else 0
    points = int(duration_hours * 10 + bonus)

    task = {
        "id": task_id_counter,
        "title": title,
        "category": category,
        "priority": priority,
        "duration_hours": duration_hours,
        "created_at": created_at,
        "due_date": due_date,
        "completed": False,
        "points": points
    }

    tasks.append(task)
    task_id_counter += 1

    return {
        "message": f"Task '{title}' added successfully",
        "points_awarded": points
    }

# -----------------------------
# 📋 List Tasks
# -----------------------------
@mcp.tool()
def list_tasks() -> list:
    return tasks

# -----------------------------
# ✅ Complete Task
# -----------------------------
@mcp.tool()
def complete_task(task_id: int) -> dict:

    for task in tasks:
        if task["id"] == task_id:
            if task["completed"]:
                return {"message": "Task already completed"}
            task["completed"] = True
            return {
                "message": f"Task {task_id} completed",
                "points_earned": task["points"]
            }

    return {"error": "Task not found"}

# -----------------------------
# ⏳ Pending Tasks
# -----------------------------
@mcp.tool()
def pending_tasks() -> list:
    return [task for task in tasks if not task["completed"]]

# -----------------------------
# 💰 Total Points
# -----------------------------
@mcp.tool()
def total_points() -> dict:
    total = sum(task["points"] for task in tasks if task["completed"])
    return {"total_points": total}

# -----------------------------
# 🔥 Streak
# -----------------------------
@mcp.tool()
def streak() -> dict:
    completed_days = sorted(
        list({
            task["created_at"][:10]
            for task in tasks
            if task["completed"]
        }),
        reverse=True
    )

    streak_count = 0
    today = date.today()

    for i, day_str in enumerate(completed_days):
        day_date = datetime.strptime(day_str, "%Y-%m-%d").date()
        if day_date == today - timedelta(days=i):
            streak_count += 1
        else:
            break

    return {"current_streak_days": streak_count}

# -----------------------------
# 🏆 Achievements
# -----------------------------
@mcp.tool()
def achievements() -> dict:
    total = total_points()["total_points"]
    streak_days = streak()["current_streak_days"]

    unlocked = []

    if total >= 50:
        unlocked.append("🥇 Rookie Productivity")
    if total >= 100:
        unlocked.append("🥈 Pro Productivity")
    if streak_days >= 3:
        unlocked.append("🔥 3-Day Streak")
    if streak_days >= 7:
        unlocked.append("💎 7-Day Streak")

    if not unlocked:
        unlocked.append("Keep going! Your journey has started 🚀")

    return {"achievements": unlocked}

# -----------------------------
# 💧 Log Water
# -----------------------------
@mcp.tool()
def log_water(amount_liters: float, log_date: str = None) -> dict:

    if not log_date:
        log_date = str(date.today())

    if log_date not in water_logs:
        water_logs[log_date] = 0

    water_logs[log_date] += amount_liters

    total = water_logs[log_date]
    status = "💧 Excellent hydration!" if total >= 2.5 else "⚠️ Drink more water."

    return {
        "date": log_date,
        "total_water": total,
        "status": status
    }

# -----------------------------
# 💡 Suggest Breaks
# -----------------------------
@mcp.tool()
def suggest_breaks() -> str:
    total_hours = sum(
        task["duration_hours"]
        for task in tasks
        if not task["completed"]
    )

    if total_hours >= 2:
        return "⚡ Long study session detected! Take a 5–10 min stretch or walk."
    return "✅ Study load is balanced. Keep going!"

# -----------------------------
# 📝 Generate Notes
# -----------------------------
@mcp.tool()
def generate_notes(topic: str) -> dict:

    notes = f"""
📌 Detailed Notes on {topic}

1️⃣ Introduction
Definition and overview of {topic}.

2️⃣ Core Concepts
- Important principles
- Key terminology
- Fundamental rules

3️⃣ Practical Applications
- Real-world use cases
- Example scenarios

4️⃣ Common Mistakes
- Conceptual misunderstandings
- Implementation errors

5️⃣ Summary
Quick revision points for exams.

6️⃣ Practice Questions
- Short answer questions
- Case-based problems
"""

    return {
        "topic": topic,
        "notes": notes.strip()
    }

# -----------------------------
# 🗑 Clear Tasks
# -----------------------------
@mcp.tool()
def clear_tasks() -> str:
    global tasks, task_id_counter
    tasks = []
    task_id_counter = 1
    return "All tasks cleared."

# -----------------------------
# 🚀 Run MCP Server
# -----------------------------
if __name__ == "__main__":
    mcp.run(transport="http", host="0.0.0.0", port=8000)