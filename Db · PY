"""
db.py
Central SQLite data layer for SchoolMind AI.

Replaces the old CSV-as-database approach (attendance.csv / fees.csv / marks.csv
read directly by pandas in analytics.py) with a real relational schema.
"""

import os
import sqlite3
import pandas as pd

DB_PATH = "schoolmind.db"


def get_connection():
    """Return a connection with foreign keys enabled and Row access by column name."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


SCHEMA = """
CREATE TABLE IF NOT EXISTS students (
    student_id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    class TEXT
);

CREATE TABLE IF NOT EXISTS attendance (
    student_id INTEGER PRIMARY KEY REFERENCES students(student_id),
    attendance_percent REAL,
    days_present INTEGER,
    days_absent INTEGER
);

CREATE TABLE IF NOT EXISTS fees (
    student_id INTEGER PRIMARY KEY REFERENCES students(student_id),
    total_fee REAL,
    paid_fee REAL,
    pending_fee REAL
);

CREATE TABLE IF NOT EXISTS marks (
    student_id INTEGER PRIMARY KEY REFERENCES students(student_id),
    maths REAL,
    science REAL,
    english REAL,
    total REAL
);

CREATE INDEX IF NOT EXISTS idx_attendance_percent ON attendance(attendance_percent);
CREATE INDEX IF NOT EXISTS idx_fees_pending ON fees(pending_fee);
CREATE INDEX IF NOT EXISTS idx_marks_total ON marks(total);
"""


def init_schema(conn):
    conn.executescript(SCHEMA)
    conn.commit()


def migrate_csv_to_sqlite(data_dir="data"):
    """
    One-time migration: reads the existing attendance/fees/marks CSVs and
    loads them into schoolmind.db. Safe to re-run (INSERT OR REPLACE).
    Call this once, then delete/ignore the CSVs for the live app.
    """
    conn = get_connection()
    init_schema(conn)
    cur = conn.cursor()

    attendance_df = pd.read_csv(os.path.join(data_dir, "attendance.csv"))
    fees_df = pd.read_csv(os.path.join(data_dir, "fees.csv"))
    marks_df = pd.read_csv(os.path.join(data_dir, "marks.csv"))

    # STUDENTS (dedup across all three files using attendance.csv as source of names/class)
    for _, row in attendance_df.iterrows():
        cur.execute(
            "INSERT OR REPLACE INTO students (student_id, name, class) VALUES (?, ?, ?)",
            (int(row["StudentID"]), row["Name"], row["Class"]),
        )

    for _, row in attendance_df.iterrows():
        cur.execute(
            """INSERT OR REPLACE INTO attendance
               (student_id, attendance_percent, days_present, days_absent)
               VALUES (?, ?, ?, ?)""",
            (
                int(row["StudentID"]),
                float(row["AttendancePercent"]),
                int(row["DaysPresent"]),
                int(row["DaysAbsent"]),
            ),
        )

    for _, row in fees_df.iterrows():
        cur.execute(
            """INSERT OR REPLACE INTO fees
               (student_id, total_fee, paid_fee, pending_fee)
               VALUES (?, ?, ?, ?)""",
            (
                int(row["StudentID"]),
                float(row["TotalFee"]),
                float(row["PaidFee"]),
                float(row["PendingFee"]),
            ),
        )

    for _, row in marks_df.iterrows():
        cur.execute(
            """INSERT OR REPLACE INTO marks
               (student_id, maths, science, english, total)
               VALUES (?, ?, ?, ?, ?)""",
            (
                int(row["StudentID"]),
                float(row["Maths"]),
                float(row["Science"]),
                float(row["English"]),
                float(row["Total"]),
            ),
        )

    conn.commit()
    conn.close()
    print("Migration complete: schoolmind.db populated from CSVs.")


if __name__ == "__main__":
    migrate_csv_to_sqlite()
