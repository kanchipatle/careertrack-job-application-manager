from flask import Flask, render_template, request, redirect, url_for, flash, Response
import sqlite3
import csv
import io
import os
from datetime import date, datetime
from pathlib import Path

app = Flask(__name__)
app.secret_key = os.environ.get("CAREERTRACK_SECRET_KEY", "dev-only-change-me")
DB_PATH = Path(__file__).with_name("careertrack.db")
STATUSES = ["Wishlist", "Applied", "Assessment", "Interview", "Selected", "Rejected"]

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def init_db():
    with get_db() as conn:
        conn.execute("""CREATE TABLE IF NOT EXISTS applications (
            id INTEGER PRIMARY KEY AUTOINCREMENT, company TEXT NOT NULL, role TEXT NOT NULL,
            location TEXT DEFAULT '', work_mode TEXT DEFAULT 'Not specified', stipend REAL,
            application_date TEXT NOT NULL, status TEXT NOT NULL DEFAULT 'Applied',
            follow_up_date TEXT, job_url TEXT DEFAULT '', notes TEXT DEFAULT '',
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP)""")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_app_status ON applications(status)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_app_company ON applications(company)")

def fetch_applications(search="", status="", sort="newest"):
    order = "application_date DESC, id DESC" if sort == "newest" else "application_date ASC, id ASC"
    sql, params = "SELECT * FROM applications WHERE 1=1", []
    if search:
        sql += " AND (company LIKE ? OR role LIKE ? OR location LIKE ?)"
        like = f"%{search}%"
        params.extend([like, like, like])
    if status and status in STATUSES:
        sql += " AND status = ?"
        params.append(status)
    with get_db() as conn:
        return conn.execute(sql + f" ORDER BY {order}", params).fetchall()

@app.route("/")
def dashboard():
    search = request.args.get("q", "").strip()
    status_filter = request.args.get("status", "").strip()
    sort = request.args.get("sort", "newest")
    applications = fetch_applications(search, status_filter, sort)
    with get_db() as conn:
        total = conn.execute("SELECT COUNT(*) FROM applications").fetchone()[0]
        active = conn.execute("SELECT COUNT(*) FROM applications WHERE status IN ('Applied','Assessment','Interview')").fetchone()[0]
        interviews = conn.execute("SELECT COUNT(*) FROM applications WHERE status='Interview'").fetchone()[0]
        selected = conn.execute("SELECT COUNT(*) FROM applications WHERE status='Selected'").fetchone()[0]
        status_rows = conn.execute("SELECT status, COUNT(*) AS count FROM applications GROUP BY status").fetchall()
        upcoming = conn.execute("""SELECT * FROM applications WHERE follow_up_date IS NOT NULL
            AND follow_up_date != '' AND follow_up_date >= ?
            AND status NOT IN ('Selected','Rejected') ORDER BY follow_up_date ASC LIMIT 5""",
            (date.today().isoformat(),)).fetchall()
    counts = {s: 0 for s in STATUSES}
    for row in status_rows:
        counts[row["status"]] = row["count"]
    return render_template("dashboard.html", applications=applications, total=total, active=active,
        interviews=interviews, selected=selected, counts=counts, upcoming=upcoming, statuses=STATUSES,
        q=search, status_filter=status_filter, sort=sort, today=date.today().isoformat())

@app.route("/add", methods=["GET", "POST"])
def add_application():
    if request.method == "POST":
        data = read_form()
        error = validate(data)
        if error:
            flash(error, "error")
            return render_template("form.html", item=data, statuses=STATUSES, page_title="Add application")
        with get_db() as conn:
            conn.execute("""INSERT INTO applications
                (company, role, location, work_mode, stipend, application_date, status, follow_up_date, job_url, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""", values(data))
        flash("Application added successfully.", "success")
        return redirect(url_for("dashboard"))
    return render_template("form.html", item={}, statuses=STATUSES, page_title="Add application")

@app.route("/edit/<int:app_id>", methods=["GET", "POST"])
def edit_application(app_id):
    with get_db() as conn:
        item = conn.execute("SELECT * FROM applications WHERE id=?", (app_id,)).fetchone()
    if not item:
        flash("Application not found.", "error")
        return redirect(url_for("dashboard"))
    if request.method == "POST":
        data = read_form()
        error = validate(data)
        if error:
            flash(error, "error")
            return render_template("form.html", item=data, statuses=STATUSES, page_title="Edit application", app_id=app_id)
        with get_db() as conn:
            conn.execute("""UPDATE applications SET company=?, role=?, location=?, work_mode=?, stipend=?,
                application_date=?, status=?, follow_up_date=?, job_url=?, notes=?, updated_at=CURRENT_TIMESTAMP
                WHERE id=?""", values(data) + [app_id])
        flash("Application updated successfully.", "success")
        return redirect(url_for("dashboard"))
    return render_template("form.html", item=dict(item), statuses=STATUSES, page_title="Edit application", app_id=app_id)

@app.route("/delete/<int:app_id>", methods=["POST"])
def delete_application(app_id):
    with get_db() as conn:
        conn.execute("DELETE FROM applications WHERE id=?", (app_id,))
    flash("Application deleted.", "success")
    return redirect(url_for("dashboard"))

@app.route("/export")
def export_csv():
    rows = fetch_applications()
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Company", "Role", "Location", "Work mode", "Stipend", "Application date",
        "Status", "Follow-up date", "Job URL", "Notes"])
    for row in rows:
        writer.writerow([row["company"], row["role"], row["location"], row["work_mode"], row["stipend"],
            row["application_date"], row["status"], row["follow_up_date"], row["job_url"], row["notes"]])
    return Response("\ufeff" + output.getvalue(), mimetype="text/csv",
        headers={"Content-Disposition": "attachment; filename=careertrack_applications.csv"})

def read_form():
    stipend_raw = request.form.get("stipend", "").strip()
    try:
        stipend = float(stipend_raw) if stipend_raw else None
    except ValueError:
        stipend = -1
    return {"company": request.form.get("company", "").strip(), "role": request.form.get("role", "").strip(),
        "location": request.form.get("location", "").strip(), "work_mode": request.form.get("work_mode", "Not specified").strip(),
        "stipend": stipend, "application_date": request.form.get("application_date", "").strip(),
        "status": request.form.get("status", "Applied").strip(), "follow_up_date": request.form.get("follow_up_date", "").strip(),
        "job_url": request.form.get("job_url", "").strip(), "notes": request.form.get("notes", "").strip()}

def validate(data):
    if not data["company"] or not data["role"] or not data["application_date"]:
        return "Company, role and application date are required."
    if data["stipend"] == -1 or (data["stipend"] is not None and data["stipend"] < 0):
        return "Enter a valid non-negative stipend amount."
    if data["status"] not in STATUSES:
        return "Choose a valid application status."
    for field in ("application_date", "follow_up_date"):
        if data[field]:
            try:
                datetime.strptime(data[field], "%Y-%m-%d")
            except ValueError:
                return f"Enter a valid {field.replace('_', ' ')}."
    return None

def values(data):
    return [data["company"], data["role"], data["location"], data["work_mode"], data["stipend"],
        data["application_date"], data["status"], data["follow_up_date"], data["job_url"], data["notes"]]

init_db()
if __name__ == "__main__":
    app.run(debug=os.environ.get("FLASK_DEBUG", "0") == "1")
