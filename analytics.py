"""
analytics.py
All dashboard/analytics functions now query schoolmind.db (SQLite) directly
instead of re-reading and merging three CSVs on every call.
"""

import pandas as pd
from db import get_connection


def get_dashboard_stats():
    conn = get_connection()

    total_students = conn.execute(
        "SELECT COUNT(*) AS c FROM students"
    ).fetchone()["c"]

    avg_attendance = conn.execute(
        "SELECT ROUND(AVG(attendance_percent), 2) AS avg_a FROM attendance"
    ).fetchone()["avg_a"]

    total_pending_fees = conn.execute(
        "SELECT SUM(pending_fee) AS total FROM fees"
    ).fetchone()["total"]

    top_row = conn.execute(
        """SELECT s.name, m.total
           FROM marks m JOIN students s ON s.student_id = m.student_id
           ORDER BY m.total DESC LIMIT 1"""
    ).fetchone()

    conn.close()
    return {
        "total_students": total_students,
        "avg_attendance": avg_attendance or 0,
        "total_pending_fees": total_pending_fees or 0,
        "top_student": top_row["name"] if top_row else None,
        "top_marks": top_row["total"] if top_row else None,
    }


def get_top_students(limit=3):
    conn = get_connection()
    df = pd.read_sql_query(
        """SELECT s.student_id, s.name, s.class, m.maths, m.science, m.english, m.total
           FROM marks m JOIN students s ON s.student_id = m.student_id
           ORDER BY m.total DESC LIMIT ?""",
        conn,
        params=(limit,),
    )
    conn.close()
    return df


def get_highest_pending_fee():
    conn = get_connection()
    row = conn.execute(
        """SELECT s.student_id, s.name, f.total_fee, f.paid_fee, f.pending_fee
           FROM fees f JOIN students s ON s.student_id = f.student_id
           ORDER BY f.pending_fee DESC LIMIT 1"""
    ).fetchone()
    conn.close()
    return dict(row) if row else None


def get_low_attendance_pending_fee():
    conn = get_connection()
    df = pd.read_sql_query(
        """SELECT s.student_id, s.name, a.attendance_percent, f.pending_fee
           FROM attendance a
           JOIN fees f ON f.student_id = a.student_id
           JOIN students s ON s.student_id = a.student_id
           WHERE a.attendance_percent < 75 AND f.pending_fee > 0""",
        conn,
    )
    conn.close()
    return df


def get_at_risk_students():
    """
    At-risk = attendance < 75% OR pending fee > 10000 OR total marks < 220.
    This is now a single indexed SQL query instead of three pandas merges.
    """
    conn = get_connection()
    df = pd.read_sql_query(
        """SELECT s.student_id, s.name,
                  a.attendance_percent AS "AttendancePercent",
                  f.pending_fee AS "PendingFee",
                  m.total AS "Total"
           FROM students s
           JOIN attendance a ON a.student_id = s.student_id
           JOIN fees f ON f.student_id = s.student_id
           JOIN marks m ON m.student_id = s.student_id
           WHERE a.attendance_percent < 75
              OR f.pending_fee > 10000
              OR m.total < 220""",
        conn,
    )
    df.insert(1, "Name", df.pop("name"))
    conn.close()
    return df


def get_all_marks():
    conn = get_connection()
    df = pd.read_sql_query(
        """SELECT s.student_id AS StudentID, s.name AS Name, s.class AS Class,
                  m.maths AS Maths, m.science AS Science, m.english AS English,
                  m.total AS Total
           FROM marks m JOIN students s ON s.student_id = m.student_id""",
        conn,
    )
    conn.close()
    return df


def get_all_fees():
    conn = get_connection()
    df = pd.read_sql_query(
        """SELECT s.student_id AS StudentID, s.name AS Name, s.class AS Class,
                  f.total_fee AS TotalFee, f.paid_fee AS PaidFee,
                  f.pending_fee AS PendingFee
           FROM fees f JOIN students s ON s.student_id = f.student_id""",
        conn,
    )
    conn.close()
    return df


def get_all_attendance():
    conn = get_connection()
    df = pd.read_sql_query(
        """SELECT s.student_id AS StudentID, s.name AS Name, s.class AS Class,
                  a.attendance_percent AS AttendancePercent,
                  a.days_present AS DaysPresent, a.days_absent AS DaysAbsent
           FROM attendance a JOIN students s ON s.student_id = a.student_id""",
        conn,
    )
    conn.close()
    return df
