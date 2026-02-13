import os
import sqlite3
from datetime import datetime, date, timedelta
from fastmcp import FastMCP

# -----------------------------
# MCP INIT
# -----------------------------
mcp = FastMCP("Life_Productivity_Wellness_Companion")

# -----------------------------
# DATABASE CONFIG
# -----------------------------
DB_PATH = os.path.join(os.path.dirname(__file__), "productivity_wellness.db")

def init_db():
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        # Tasks table
        c.execute("""
        CREATE TABLE IF NOT EXISTS tasks(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            category TEXT DEFAULT 'Study',  -- Study / Exercise / Break
            priority TEXT DEFAULT 'Medium',
            duration_hours REAL NOT NULL,
            created_at TEXT NOT NULL,
            due_date TEXT,
            completed INTEGER DEFAULT 0,
            points INTEGER DEFAULT 0
        )
        """)
        # Hydration logs
        c.execute("""
        CREATE TABLE IF NOT EXISTS water_logs(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            log_date TEXT UNIQUE,
            water_liters REAL DEFAULT 0
        )
        """)
init_db()

# -----------------------------
# ➕ Add Task
# -----------------------------
@mcp.tool()
def add_task(title: str, duration_hours: float, category: str = "Study", priority: str = "Medium", due_date: str = None) -> str:
    """Add a task with points based on duration and priority."""
    created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    points = int(duration_hours * 10 + (5 if priority.lower() == "high" else 0))
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        c.execute("""
            INSERT INTO tasks (title, category, priority, duration_hours, created_at, due_date, completed, points)
            VALUES (?, ?, ?, ?, ?, ?, 0, ?)
        """, (title, category, priority, duration_hours, created_at, due_date, points))
        conn.commit()
    return f"Task '{title}' added in category '{category}' with {points} points."

# -----------------------------
# 📋 List Tasks
# -----------------------------
@mcp.tool()
def list_tasks() -> list:
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        c.execute("SELECT * FROM tasks ORDER BY created_at")
        rows = c.fetchall()
    return [
        {"id": r[0], "title": r[1], "category": r[2], "priority": r[3],
         "duration_hours": r[4], "created_at": r[5], "due_date": r[6],
         "completed": bool(r[7]), "points": r[8]}
        for r in rows
    ]

# -----------------------------
# ✅ Complete Task
# -----------------------------
@mcp.tool()
def complete_task(task_id: int) -> str:
    """Mark a task as completed and award points."""
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        c.execute("SELECT completed, points FROM tasks WHERE id=?", (task_id,))
        row = c.fetchone()
        if not row:
            return "Task not found."
        if row[0] == 1:
            return "Task already completed."
        points = row[1]
        c.execute("UPDATE tasks SET completed=1 WHERE id=?", (task_id,))
        conn.commit()
    return f"Task {task_id} completed! You earned {points} points 🎉."

# -----------------------------
# ⏳ Pending Tasks
# -----------------------------
@mcp.tool()
def pending_tasks() -> list:
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        c.execute("SELECT * FROM tasks WHERE completed=0 ORDER BY priority DESC, due_date ASC")
        rows = c.fetchall()
    return [
        {"id": r[0], "title": r[1], "category": r[2], "priority": r[3],
         "duration_hours": r[4], "created_at": r[5], "due_date": r[6],
         "completed": bool(r[7]), "points": r[8]}
        for r in rows
    ]

# -----------------------------
# 💰 Total Points
# -----------------------------
@mcp.tool()
def total_points() -> dict:
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        c.execute("SELECT SUM(points) FROM tasks WHERE completed=1")
        total = c.fetchone()[0] or 0
    return {"total_points": total}

# -----------------------------
# 🔥 Study & Wellness Streak
# -----------------------------
@mcp.tool()
def streak() -> dict:
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        c.execute("SELECT DISTINCT substr(created_at,1,10) as day FROM tasks WHERE completed=1 ORDER BY day DESC")
        days = [r[0] for r in c.fetchall()]
    streak = 0
    today = date.today()
    for i, day_str in enumerate(days):
        day_date = datetime.strptime(day_str, "%Y-%m-%d").date()
        if day_date == today - timedelta(days=i):
            streak += 1
        else:
            break
    return {"current_streak_days": streak}

# -----------------------------
# 🏆 Achievements
# -----------------------------
@mcp.tool()
def achievements() -> dict:
    total = total_points()["total_points"]
    streak_days = streak()["current_streak_days"]
    unlocked = []
    if total >= 50:
        unlocked.append("🥇 Rookie Productivity: Earn 50 points")
    if total >= 100:
        unlocked.append("🥈 Pro Productivity: Earn 100 points")
    if streak_days >= 3:
        unlocked.append("🔥 3-Day Streak")
    if streak_days >= 7:
        unlocked.append("💎 7-Day Streak")
    if not unlocked:
        unlocked.append("Keep being productive and hydrated!")
    return {"achievements_unlocked": unlocked}

# -----------------------------
# 💧 Log Water Intake
# -----------------------------
@mcp.tool()
def log_water(amount_liters: float, log_date: str = None) -> dict:
    if not log_date:
        log_date = str(date.today())
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        record = c.execute("SELECT id FROM water_logs WHERE log_date=?", (log_date,)).fetchone()
        if not record:
            c.execute("INSERT INTO water_logs(log_date, water_liters) VALUES (?,?)", (log_date, amount_liters))
        else:
            c.execute("UPDATE water_logs SET water_liters = water_liters + ? WHERE log_date=?", (amount_liters, log_date))
        total = c.execute("SELECT water_liters FROM water_logs WHERE log_date=?", (log_date,)).fetchone()[0]
    status = "💧 Excellent hydration!" if total >= 2.5 else "⚠️ Drink more water."
    return {"date": log_date, "total_water": total, "status": status}

# -----------------------------
# 💡 Suggest Breaks / Stretching
# -----------------------------
@mcp.tool()
def suggest_breaks() -> str:
    pending = pending_tasks()
    total_hours = sum(task["duration_hours"] for task in pending)
    if total_hours >= 2:
        return "⚡ You have long study sessions pending! Take a 5–10 min stretch or walk now."
    return "✅ Study load is light. Keep going!"

# -----------------------------
# 📝 Generate Detailed Notes
# -----------------------------
@mcp.tool()
def generate_notes(topic: str) -> dict:
    """Generate detailed study notes for a topic."""
    notes = f"📌 Detailed Notes on {topic}:\n" \
            f"- Introduction to {topic}\n" \
            f"- Key concepts and definitions\n" \
            f"- Important examples and practical applications\n" \
            f"- Common mistakes to avoid\n" \
            f"- Summary and takeaways\n" \
            f"- Suggested exercises for practice"
    return {"topic": topic, "notes": notes}

# -----------------------------
# 🗑 Clear All Tasks
# -----------------------------
@mcp.tool()
def clear_tasks() -> str:
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        c.execute("DELETE FROM tasks")
        conn.commit()
    return "All tasks cleared."

# -----------------------------
# 🚀 Run MCP Server
# -----------------------------
if __name__ == "__main__":
    mcp.run(transport="http", host="0.0.0.0",port=8000)