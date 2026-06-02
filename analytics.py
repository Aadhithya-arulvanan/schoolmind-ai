import pandas as pd

attendance_df = pd.read_csv(
    "data/attendance.csv"
)

fees_df = pd.read_csv(
    "data/fees.csv"
)

marks_df = pd.read_csv(
    "data/marks.csv"
)
def get_dashboard_stats():

    total_students = len(attendance_df)

    avg_attendance = round(
        attendance_df["AttendancePercent"].mean(),
        2
    )

    total_pending_fees = fees_df[
        "PendingFee"
    ].sum()

    top_student = marks_df.sort_values(
        "Total",
        ascending=False
    ).iloc[0]

    return {
        "total_students": total_students,
        "avg_attendance": avg_attendance,
        "total_pending_fees": total_pending_fees,
        "top_student": top_student["Name"],
        "top_marks": top_student["Total"]
    }

def get_top_students():

    return marks_df.sort_values(
        "Total",
        ascending=False
    ).head(3)

def get_highest_pending_fee():

    return fees_df.loc[
        fees_df["PendingFee"].idxmax()
    ]

def get_low_attendance_pending_fee():

    low_attendance = attendance_df[
        attendance_df["AttendancePercent"] < 75
    ]

    pending_fees = fees_df[
        fees_df["PendingFee"] > 0
    ]

    return low_attendance.merge(
        pending_fees,
        on="StudentID"
    )
def get_at_risk_students():

    merged = attendance_df.merge(
        fees_df,
        on="StudentID"
    ).merge(
        marks_df,
        on="StudentID"
    )

    result = merged[
        (merged["AttendancePercent"] < 75)
        |
        (merged["PendingFee"] > 10000)
        |
        (merged["Total"] < 220)
    ]

    return result
def get_all_marks():
    return marks_df


def get_all_fees():
    return fees_df


def get_all_attendance():
    return attendance_df