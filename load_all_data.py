import pandas as pd
import chromadb

# Create / connect to database
client = chromadb.PersistentClient(
    path="./chroma_db"
)

# Create collection
collection = client.get_or_create_collection(
    name="school_data"
)

# -----------------------------
# ATTENDANCE
# -----------------------------

attendance_df = pd.read_csv(
    "data/attendance.csv"
)

for _, row in attendance_df.iterrows():

    text = f"""
Type: Attendance

Student Name: {row['Name']}
Student ID: {row['StudentID']}
Class: {row['Class']}
Attendance Percentage: {row['AttendancePercent']}
Days Present: {row['DaysPresent']}
Days Absent: {row['DaysAbsent']}
"""

    collection.add(
        documents=[text],
        ids=[f"attendance_{row['StudentID']}"],
        metadatas=[{
            "type": "attendance",
            "student_id": str(row["StudentID"])
        }]
    )

# -----------------------------
# FEES
# -----------------------------

fees_df = pd.read_csv(
    "data/fees.csv"
)

for _, row in fees_df.iterrows():

    text = f"""
Type: Fees

Student Name: {row['Name']}
Student ID: {row['StudentID']}
Class: {row['Class']}
Total Fee: {row['TotalFee']}
Paid Fee: {row['PaidFee']}
Pending Fee: {row['PendingFee']}
"""

    collection.add(
        documents=[text],
        ids=[f"fees_{row['StudentID']}"],
        metadatas=[{
            "type": "fees",
            "student_id": str(row["StudentID"])
        }]
    )

# -----------------------------
# MARKS
# -----------------------------

marks_df = pd.read_csv(
    "data/marks.csv"
)

for _, row in marks_df.iterrows():

    text = f"""
Type: Marks

Student Name: {row['Name']}
Student ID: {row['StudentID']}
Class: {row['Class']}
Maths: {row['Maths']}
Science: {row['Science']}
English: {row['English']}
Total Marks: {row['Total']}
"""

    collection.add(
        documents=[text],
        ids=[f"marks_{row['StudentID']}"],
        metadatas=[{
            "type": "marks",
            "student_id": str(row["StudentID"])
        }]
    )

print("All data loaded successfully!")

print(
    "Total records:",
    collection.count()
)