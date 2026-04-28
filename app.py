from __future__ import annotations

import json
import os
import re
import sqlite3
from contextlib import closing
from datetime import date, datetime, timedelta
from functools import wraps
from html import escape
from io import BytesIO
from pathlib import Path
from typing import Any, Callable

from flask import (
    Flask,
    flash,
    g,
    redirect,
    render_template,
    request,
    send_file,
    session,
    url_for,
)
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle
from werkzeug.security import check_password_hash, generate_password_hash

from ai_engine import generate_meal_recommendations
from recipe_api import search_recipe_api


BASE_DIR = Path(__file__).resolve().parent
DATABASE = Path(os.environ.get("NUTRIMIND_DATABASE", BASE_DIR / "diet_planner.db"))

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("NUTRIMIND_SECRET_KEY", "dev-secret-change-before-hosting")

VALID_DIETS = {"veg", "eggetarian", "non_veg"}
VALID_GOALS = {"general_fitness", "weight_loss", "muscle_gain", "maintenance", "recovery"}
VALID_MEAL_TYPES = {"breakfast", "lunch", "dinner", "snack"}
EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


# ------------------------
# Database helpers
# ------------------------
def get_db() -> sqlite3.Connection:
    if "db" not in g:
        conn = sqlite3.connect(DATABASE)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        g.db = conn
    return g.db


@app.teardown_appcontext
def close_db(exception: Exception | None) -> None:
    db = g.pop("db", None)
    if db is not None:
        db.close()


SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    full_name TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    age INTEGER,
    gender TEXT,
    height_cm REAL,
    weight_kg REAL,
    diet_preference TEXT DEFAULT 'veg',
    goal TEXT DEFAULT 'general_fitness',
    allergies TEXT DEFAULT '',
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS daily_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    log_date TEXT NOT NULL,
    steps INTEGER DEFAULT 0,
    water_liters REAL DEFAULT 0,
    weight_kg REAL,
    kitchen_items TEXT DEFAULT '',
    meal_type TEXT DEFAULT 'breakfast',
    meal_name TEXT DEFAULT '',
    meal_json TEXT DEFAULT '',
    notes TEXT DEFAULT '',
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    UNIQUE(user_id, log_date),
    FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_daily_logs_user_date ON daily_logs(user_id, log_date);
"""


def init_db() -> None:
    DATABASE.parent.mkdir(parents=True, exist_ok=True)
    db = sqlite3.connect(DATABASE)
    try:
        db.execute("PRAGMA foreign_keys = ON")
        with closing(db.cursor()) as cur:
            cur.executescript(SCHEMA_SQL)
        db.commit()
    finally:
        db.close()


# ------------------------
# Validation helpers
# ------------------------
def parse_int(value: str | None, field_name: str, *, minimum: int | None = None, maximum: int | None = None, required: bool = False) -> int | None:
    if value is None or str(value).strip() == "":
        if required:
            raise ValueError(f"{field_name} is required.")
        return None
    try:
        parsed = int(float(str(value)))
    except ValueError as exc:
        raise ValueError(f"{field_name} must be a number.") from exc
    if minimum is not None and parsed < minimum:
        raise ValueError(f"{field_name} must be at least {minimum}.")
    if maximum is not None and parsed > maximum:
        raise ValueError(f"{field_name} must be at most {maximum}.")
    return parsed


def parse_float(value: str | None, field_name: str, *, minimum: float | None = None, maximum: float | None = None, required: bool = False) -> float | None:
    if value is None or str(value).strip() == "":
        if required:
            raise ValueError(f"{field_name} is required.")
        return None
    try:
        parsed = float(str(value))
    except ValueError as exc:
        raise ValueError(f"{field_name} must be a number.") from exc
    if minimum is not None and parsed < minimum:
        raise ValueError(f"{field_name} must be at least {minimum}.")
    if maximum is not None and parsed > maximum:
        raise ValueError(f"{field_name} must be at most {maximum}.")
    return round(parsed, 1)


def clean_choice(value: str | None, allowed: set[str], default: str) -> str:
    return value if value in allowed else default


def safe_iso_date(value: str | None) -> str:
    if not value:
        return date.today().isoformat()
    try:
        return date.fromisoformat(value).isoformat()
    except ValueError:
        return date.today().isoformat()


# ------------------------
# Auth and user helpers
# ------------------------
def current_user() -> sqlite3.Row | None:
    if "current_user" in g:
        return g.current_user

    user_id = session.get("user_id")
    if not user_id:
        g.current_user = None
        return None

    g.current_user = get_db().execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
    return g.current_user


@app.context_processor
def inject_globals() -> dict[str, Any]:
    return {"current_user": current_user(), "today": date.today().isoformat()}


def login_required() -> Callable:
    def decorator(view_func: Callable) -> Callable:
        @wraps(view_func)
        def wrapped_view(*args: Any, **kwargs: Any) -> Any:
            if not current_user():
                flash("Please log in first.", "warning")
                return redirect(url_for("login"))
            return view_func(*args, **kwargs)

        return wrapped_view

    return decorator


# ------------------------
# Dashboard calculations
# ------------------------
def get_or_create_log(user_id: int, log_date: str) -> sqlite3.Row:
    db = get_db()
    row = db.execute(
        "SELECT * FROM daily_logs WHERE user_id = ? AND log_date = ?",
        (user_id, log_date),
    ).fetchone()
    if row:
        return row

    now = datetime.now().isoformat(timespec="seconds")
    db.execute(
        """
        INSERT INTO daily_logs (user_id, log_date, created_at, updated_at)
        VALUES (?, ?, ?, ?)
        """,
        (user_id, log_date, now, now),
    )
    db.commit()
    return db.execute(
        "SELECT * FROM daily_logs WHERE user_id = ? AND log_date = ?",
        (user_id, log_date),
    ).fetchone()


def fetch_last_seven_days(user_id: int) -> list[sqlite3.Row | None]:
    start_date = (date.today() - timedelta(days=6)).isoformat()
    db = get_db()
    rows = db.execute(
        """
        SELECT * FROM daily_logs
        WHERE user_id = ? AND log_date >= ?
        ORDER BY log_date ASC
        """,
        (user_id, start_date),
    ).fetchall()

    indexed = {row["log_date"]: row for row in rows}
    result: list[sqlite3.Row | None] = []
    for offset in range(7):
        day = (date.today() - timedelta(days=6 - offset)).isoformat()
        result.append(indexed.get(day))
    return result


def profile_insights(user: sqlite3.Row) -> dict[str, Any]:
    height = float(user["height_cm"] or 0)
    weight = float(user["weight_kg"] or 0)
    age = int(user["age"] or 0)
    gender = (user["gender"] or "").lower()
    goal = user["goal"] or "general_fitness"

    bmi = None
    bmi_label = "Add height/weight"
    if height > 0 and weight > 0:
        bmi = round(weight / ((height / 100) ** 2), 1)
        if bmi < 18.5:
            bmi_label = "Underweight"
        elif bmi < 25:
            bmi_label = "Healthy range"
        elif bmi < 30:
            bmi_label = "Overweight"
        else:
            bmi_label = "Obesity range"

    calorie_target = "Add profile"
    if height > 0 and weight > 0 and age > 0:
        gender_adjustment = 5 if gender == "male" else -161 if gender == "female" else -78
        bmr = (10 * weight) + (6.25 * height) - (5 * age) + gender_adjustment
        target = int(bmr * 1.35)
        if goal == "weight_loss":
            target -= 300
        elif goal == "muscle_gain":
            target += 300
        calorie_target = f"{max(target, 1200)} kcal"

    water_target = 2.2
    if weight > 0:
        water_target = round(max(1.8, min(4.2, weight * 0.035)), 1)

    step_targets = {
        "weight_loss": 9000,
        "muscle_gain": 7500,
        "maintenance": 8000,
        "recovery": 5500,
        "general_fitness": 8000,
    }

    return {
        "bmi": bmi,
        "bmi_label": bmi_label,
        "calorie_target": calorie_target,
        "water_target": water_target,
        "step_target": step_targets.get(goal, 8000),
    }


def dashboard_summary(user: sqlite3.Row) -> dict[str, Any]:
    db = get_db()
    today_str = date.today().isoformat()
    today_log = get_or_create_log(user["id"], today_str)
    last_seven = fetch_last_seven_days(user["id"])

    filled_logs = [row for row in last_seven if row is not None]
    avg_steps = 0
    avg_water = 0.0
    if filled_logs:
        avg_steps = int(sum(int(row["steps"] or 0) for row in filled_logs) / len(filled_logs))
        avg_water = round(sum(float(row["water_liters"] or 0) for row in filled_logs) / len(filled_logs), 1)

    latest_meal = db.execute(
        """
        SELECT meal_name FROM daily_logs
        WHERE user_id = ? AND meal_name != ''
        ORDER BY log_date DESC LIMIT 1
        """,
        (user["id"],),
    ).fetchone()

    insights = profile_insights(user)

    return {
        "today_log": today_log,
        "last_seven": last_seven,
        "avg_steps": avg_steps,
        "avg_water": avg_water,
        "latest_meal": latest_meal["meal_name"] if latest_meal else "No meal generated yet",
        "insights": insights,
    }


def progress_bars(last_seven: list[sqlite3.Row | None], step_target: int = 8000) -> list[dict[str, Any]]:
    bars: list[dict[str, Any]] = []
    step_target = max(step_target, 1)

    for offset, row in enumerate(last_seven):
        day = date.today() - timedelta(days=6 - offset)
        steps = int(row["steps"] or 0) if row else 0
        water = float(row["water_liters"] or 0) if row else 0
        percentage = min(100, int((steps / step_target) * 100)) if steps else 0
        bars.append(
            {
                "label": day.strftime("%a"),
                "date": day.strftime("%d %b"),
                "steps": steps,
                "water": water,
                "percentage": max(8, percentage) if steps else 8,
                "meal": row["meal_name"] if row and row["meal_name"] else "—",
            }
        )
    return bars


def create_realistic_week(user: sqlite3.Row) -> None:
    """Create realistic generated logs from the current profile for a presentation-ready sample week."""
    db = get_db()
    now = datetime.now().isoformat(timespec="seconds")
    goal = user["goal"] or "general_fitness"
    diet = user["diet_preference"] or "veg"
    allergies = user["allergies"] or ""
    weight = float(user["weight_kg"] or 65)

    kitchen_sets = [
        ("oats, banana, curd, apple", "breakfast"),
        ("paneer, roti, onion, tomato, capsicum", "lunch"),
        ("rice, dal, carrot, peas", "dinner"),
        ("besan, onion, tomato, curd", "breakfast"),
        ("chana, cucumber, tomato, lemon", "snack"),
        ("soya, rice, peas, carrot", "lunch"),
        ("curd, apple, almond, honey", "snack"),
    ]
    if diet == "eggetarian":
        kitchen_sets[3] = ("egg, bread, onion, tomato", "breakfast")
        kitchen_sets[5] = ("egg, rice, peas, carrot", "dinner")
    elif diet == "non_veg":
        kitchen_sets[1] = ("chicken, roti, onion, tomato, cucumber", "lunch")
        kitchen_sets[5] = ("chicken, rice, curd, cucumber", "lunch")

    base_steps = {
        "weight_loss": 7600,
        "muscle_gain": 6500,
        "maintenance": 7000,
        "recovery": 4300,
        "general_fitness": 6800,
    }.get(goal, 6800)

    for offset, (items, meal_type) in enumerate(kitchen_sets):
        day_index = 6 - offset
        log_date = (date.today() - timedelta(days=day_index)).isoformat()
        steps = base_steps + (offset * 430) + ((offset % 3) * 280)
        water = round(1.8 + (offset * 0.13), 1)
        weight_for_day = round(weight - max(0, offset - 1) * 0.08, 1)
        payload = generate_meal_recommendations(items, meal_type, diet, goal, allergies)
        recommendations = payload.get("recommendations", [])
        meal_name = recommendations[0]["name"] if recommendations else "Personalized Balanced Plate"

        db.execute(
            """
            INSERT INTO daily_logs (
                user_id, log_date, steps, water_liters, weight_kg, kitchen_items,
                meal_type, meal_name, meal_json, notes, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(user_id, log_date) DO UPDATE SET
                steps = excluded.steps,
                water_liters = excluded.water_liters,
                weight_kg = excluded.weight_kg,
                kitchen_items = excluded.kitchen_items,
                meal_type = excluded.meal_type,
                meal_name = excluded.meal_name,
                meal_json = excluded.meal_json,
                notes = excluded.notes,
                updated_at = excluded.updated_at
            """,
            (
                user["id"],
                log_date,
                steps,
                water,
                weight_for_day,
                items,
                meal_type,
                meal_name,
                json.dumps(payload),
                "Generated realistic sample week from this user profile",
                now,
                now,
            ),
        )
    db.commit()


# ------------------------
# Routes
# ------------------------
@app.route("/")
def index() -> str:
    if current_user():
        return redirect(url_for("dashboard"))
    return render_template("index.html")


@app.route("/signup", methods=["GET", "POST"])
def signup() -> str:
    if request.method == "POST":
        full_name = request.form.get("full_name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        gender = request.form.get("gender", "")
        diet_preference = clean_choice(request.form.get("diet_preference"), VALID_DIETS, "veg")
        goal = clean_choice(request.form.get("goal"), VALID_GOALS, "general_fitness")
        allergies = request.form.get("allergies", "").strip()

        try:
            age = parse_int(request.form.get("age"), "Age", minimum=5, maximum=110)
            height_cm = parse_float(request.form.get("height_cm"), "Height", minimum=80, maximum=250)
            weight_kg = parse_float(request.form.get("weight_kg"), "Weight", minimum=20, maximum=250)
        except ValueError as exc:
            flash(str(exc), "danger")
            return render_template("signup.html")

        if not full_name or not email or not password:
            flash("Name, email, and password are required.", "danger")
            return render_template("signup.html")
        if not EMAIL_RE.match(email):
            flash("Please enter a valid email address.", "danger")
            return render_template("signup.html")
        if len(password) < 6:
            flash("Password must be at least 6 characters for account safety.", "danger")
            return render_template("signup.html")

        db = get_db()
        existing = db.execute("SELECT id FROM users WHERE email = ?", (email,)).fetchone()
        if existing:
            flash("This email is already registered. Please log in.", "warning")
            return redirect(url_for("login"))

        db.execute(
            """
            INSERT INTO users (
                full_name, email, password_hash, age, gender, height_cm, weight_kg,
                diet_preference, goal, allergies, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                full_name,
                email,
                generate_password_hash(password),
                age,
                gender,
                height_cm,
                weight_kg,
                diet_preference,
                goal,
                allergies,
                datetime.now().isoformat(timespec="seconds"),
            ),
        )
        db.commit()
        flash("Account created successfully. Please log in.", "success")
        return redirect(url_for("login"))

    return render_template("signup.html")


@app.route("/login", methods=["GET", "POST"])
def login() -> str:
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        db = get_db()
        user = db.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()

        if not user or not check_password_hash(user["password_hash"], password):
            flash("Invalid email or password.", "danger")
            return render_template("login.html")

        session.clear()
        session["user_id"] = user["id"]
        flash(f"Welcome back, {user['full_name'].split()[0]}!", "success")
        return redirect(url_for("dashboard"))

    return render_template("login.html")


@app.route("/logout")
def logout() -> str:
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for("index"))


@app.route("/dashboard")
@login_required()
def dashboard() -> str:
    user = current_user()
    assert user is not None
    summary = dashboard_summary(user)
    bars = progress_bars(summary["last_seven"], summary["insights"]["step_target"])

    latest_meal_payload = None
    if summary["today_log"] and summary["today_log"]["meal_json"]:
        try:
            latest_meal_payload = json.loads(summary["today_log"]["meal_json"])
        except json.JSONDecodeError:
            latest_meal_payload = None

    return render_template(
        "dashboard.html",
        summary=summary,
        bars=bars,
        meal_payload=latest_meal_payload,
    )


@app.route("/profile", methods=["GET", "POST"])
@login_required()
def profile() -> str:
    user = current_user()
    assert user is not None

    if request.method == "POST":
        try:
            age = parse_int(request.form.get("age"), "Age", minimum=5, maximum=110)
            height_cm = parse_float(request.form.get("height_cm"), "Height", minimum=80, maximum=250)
            weight_kg = parse_float(request.form.get("weight_kg"), "Weight", minimum=20, maximum=250)
        except ValueError as exc:
            flash(str(exc), "danger")
            return redirect(url_for("profile"))

        full_name = request.form.get("full_name", "").strip()
        if not full_name:
            flash("Full name cannot be empty.", "danger")
            return redirect(url_for("profile"))

        db = get_db()
        db.execute(
            """
            UPDATE users
            SET full_name = ?, age = ?, gender = ?, height_cm = ?, weight_kg = ?,
                diet_preference = ?, goal = ?, allergies = ?
            WHERE id = ?
            """,
            (
                full_name,
                age,
                request.form.get("gender", ""),
                height_cm,
                weight_kg,
                clean_choice(request.form.get("diet_preference"), VALID_DIETS, "veg"),
                clean_choice(request.form.get("goal"), VALID_GOALS, "general_fitness"),
                request.form.get("allergies", "").strip(),
                user["id"],
            ),
        )
        db.commit()
        g.pop("current_user", None)
        flash("Profile updated successfully.", "success")
        return redirect(url_for("profile"))

    return render_template("profile.html", user=user)


@app.route("/generate-meal", methods=["POST"])
@login_required()
def generate_meal() -> str:
    user = current_user()
    assert user is not None
    kitchen_items = request.form.get("kitchen_items", "").strip()
    meal_type = clean_choice(request.form.get("meal_type"), VALID_MEAL_TYPES, "breakfast")
    diet_preference = clean_choice(request.form.get("diet_preference") or user["diet_preference"], VALID_DIETS, "veg")
    goal = clean_choice(request.form.get("goal") or user["goal"], VALID_GOALS, "general_fitness")

    if len(kitchen_items) < 2:
        flash("Add at least two kitchen items so the AI engine can rank meals properly.", "warning")
        return redirect(url_for("dashboard"))

    payload = generate_meal_recommendations(kitchen_items, meal_type, diet_preference, goal, user["allergies"] or "")
    external_payload = search_recipe_api(kitchen_items, meal_type, diet_preference, goal, user["allergies"] or "")
    payload["external_api"] = external_payload

    if not payload["recommendations"] and not external_payload.get("recipes"):
        flash(payload.get("summary", "No safe meal could be generated. Please adjust items or allergies."), "warning")
        return redirect(url_for("dashboard"))

    top_meal = payload["recommendations"][0] if payload["recommendations"] else external_payload["recipes"][0]
    today_str = safe_iso_date(request.form.get("log_date"))
    db = get_db()
    get_or_create_log(user["id"], today_str)
    db.execute(
        """
        UPDATE daily_logs
        SET kitchen_items = ?, meal_type = ?, meal_name = ?, meal_json = ?, updated_at = ?
        WHERE user_id = ? AND log_date = ?
        """,
        (
            kitchen_items,
            meal_type,
            top_meal["name"],
            json.dumps(payload),
            datetime.now().isoformat(timespec="seconds"),
            user["id"],
            today_str,
        ),
    )
    db.commit()
    if external_payload.get("status") == "success":
        flash("AI meal recommendations generated with live recipe API results.", "success")
    elif external_payload.get("status") == "disabled":
        flash("AI meal recommendations generated. Add SPOONACULAR_API_KEY to enable live recipe API results.", "info")
    else:
        flash("AI meal recommendations generated. Live recipe API was unavailable, so offline results were used.", "warning")
    return redirect(url_for("dashboard"))


@app.route("/save-progress", methods=["POST"])
@login_required()
def save_progress() -> str:
    user = current_user()
    assert user is not None

    log_date = safe_iso_date(request.form.get("log_date"))
    try:
        steps = parse_int(request.form.get("steps"), "Steps", minimum=0, maximum=100000, required=True)
        water_liters = parse_float(request.form.get("water_liters"), "Water", minimum=0, maximum=10, required=True)
        weight_kg = parse_float(request.form.get("weight_kg"), "Weight", minimum=20, maximum=250)
    except ValueError as exc:
        flash(str(exc), "danger")
        return redirect(url_for("dashboard"))

    notes = request.form.get("notes", "").strip()[:250]

    get_or_create_log(user["id"], log_date)
    db = get_db()
    db.execute(
        """
        UPDATE daily_logs
        SET steps = ?, water_liters = ?, weight_kg = ?, notes = ?, updated_at = ?
        WHERE user_id = ? AND log_date = ?
        """,
        (
            steps,
            water_liters,
            weight_kg,
            notes,
            datetime.now().isoformat(timespec="seconds"),
            user["id"],
            log_date,
        ),
    )
    db.commit()
    flash("Daily progress saved.", "success")
    return redirect(url_for("dashboard"))


@app.route("/save-steps", methods=["POST"])
@login_required()
def save_steps() -> str:
    user = current_user()
    assert user is not None
    try:
        steps = parse_int(request.form.get("steps"), "Steps", minimum=0, maximum=100000, required=True)
    except ValueError as exc:
        flash(str(exc), "danger")
        return redirect(url_for("dashboard"))

    today_str = date.today().isoformat()
    get_or_create_log(user["id"], today_str)

    db = get_db()
    db.execute(
        """
        UPDATE daily_logs
        SET steps = ?, updated_at = ?
        WHERE user_id = ? AND log_date = ?
        """,
        (
            steps,
            datetime.now().isoformat(timespec="seconds"),
            user["id"],
            today_str,
        ),
    )
    db.commit()
    flash("Step counter synced to today's record.", "success")
    return redirect(url_for("dashboard"))


@app.route("/prepare-sample-week", methods=["POST"])
@login_required()
def prepare_sample_week() -> str:
    user = current_user()
    assert user is not None
    create_realistic_week(user)
    flash("Sample week prepared: realistic 7-day progress, meals, hydration, and steps were generated from this profile.", "success")
    return redirect(url_for("dashboard"))


@app.route("/download-report")
@login_required()
def download_report() -> Any:
    user = current_user()
    assert user is not None
    insights = profile_insights(user)
    bars = progress_bars(fetch_last_seven_days(user["id"]), insights["step_target"])
    latest_log = get_db().execute(
        "SELECT * FROM daily_logs WHERE user_id = ? ORDER BY log_date DESC LIMIT 1",
        (user["id"],),
    ).fetchone()

    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, title="NutriMind AI Report")
    styles = getSampleStyleSheet()
    content: list[Any] = []

    content.append(Paragraph("NutriMind AI - 7 Day Progress Report", styles["Title"]))
    content.append(Spacer(1, 12))
    content.append(
        Paragraph(
            f"<b>Name:</b> {escape(user['full_name'])} &nbsp;&nbsp;&nbsp; <b>Email:</b> {escape(user['email'])}",
            styles["Normal"],
        )
    )
    content.append(
        Paragraph(
            f"<b>Diet:</b> {escape(user['diet_preference'].replace('_', ' ').title())} &nbsp;&nbsp;&nbsp; "
            f"<b>Goal:</b> {escape(user['goal'].replace('_', ' ').title())}",
            styles["Normal"],
        )
    )
    content.append(
        Paragraph(
            f"<b>BMI:</b> {insights['bmi'] or 'Not available'} ({escape(insights['bmi_label'])}) &nbsp;&nbsp;&nbsp; "
            f"<b>Calorie Target:</b> {escape(str(insights['calorie_target']))}",
            styles["Normal"],
        )
    )
    content.append(Spacer(1, 14))

    table_data = [["Day", "Date", "Steps", "Water (L)", "Meal"]]
    for entry in bars:
        table_data.append(
            [
                entry["label"],
                entry["date"],
                str(entry["steps"]),
                str(entry["water"]),
                escape(entry["meal"]),
            ]
        )

    table = Table(table_data, repeatRows=1, colWidths=[48, 68, 70, 72, 220])
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0b5cff")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.whitesmoke, colors.lightgrey]),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ]
        )
    )
    content.append(table)
    content.append(Spacer(1, 16))

    if latest_log and latest_log["meal_name"]:
        content.append(Paragraph("Latest AI Meal Recommendation", styles["Heading2"]))
        content.append(Paragraph(f"<b>Meal:</b> {escape(latest_log['meal_name'])}", styles["Normal"]))
        if latest_log["meal_json"]:
            try:
                meal_payload = json.loads(latest_log["meal_json"])
                summary = meal_payload.get("summary", "")
                if summary:
                    content.append(Paragraph(escape(summary), styles["BodyText"]))
                recommendations = meal_payload.get("recommendations") or []
                if recommendations:
                    top = recommendations[0]
                    if top.get("health_score"):
                        content.append(Paragraph(f"<b>Meal Score:</b> {escape(str(top['health_score']))}/100", styles["Normal"]))
                    if top.get("explanation"):
                        content.append(Paragraph(f"<b>AI Explanation:</b> {escape(top['explanation'])}", styles["BodyText"]))
            except json.JSONDecodeError:
                pass

    doc.build(content)
    buffer.seek(0)
    filename = f"NutriMind_AI_Report_{date.today().isoformat()}.pdf"
    return send_file(buffer, as_attachment=True, download_name=filename, mimetype="application/pdf")


@app.route("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "app": "NutriMind AI"}


init_db()

if __name__ == "__main__":
    app.run(debug=True)
