"""
load_all_data.py
Populates the ChromaDB vector store from schoolmind.db (SQLite) — not from CSVs.
SQLite is now the single source of truth; Chroma is a derived index used only
for semantic name/record lookup (see chroma_tools.py), never for structured
queries like "who has pending fees."
"""

import chromadb
from db import get_connection

client = chromadb.PersistentClient(path="./chroma_db")
collection = client.get_or_create_collection(name="school_data")

conn = get_connection()

rows = conn.execute(
    """SELECT s.student_id, s.name, s.class,
              a.attendance_percent, a.days_present, a.days_absent,
              f.total_fee, f.paid_fee, f.pending_fee,
              m.maths, m.science, m.english, m.total
       FROM students s
       JOIN attendance a ON a.student_id = s.student_id
       JOIN fees f ON f.student_id = s.student_id
       JOIN marks m ON m.student_id = s.student_id"""
).fetchall()

for row in rows:
    student_id = row["student_id"]

    attendance_text = f"""
Type: Attendance
Student Name: {row['name']}
Student ID: {student_id}
Class: {row['class']}
Attendance Percentage: {row['attendance_percent']}
Days Present: {row['days_present']}
Days Absent: {row['days_absent']}
"""
    fees_text = f"""
Type: Fees
Student Name: {row['name']}
Student ID: {student_id}
Class: {row['class']}
Total Fee: {row['total_fee']}
Paid Fee: {row['paid_fee']}
Pending Fee: {row['pending_fee']}
"""
    marks_text = f"""
Type: Marks
Student Name: {row['name']}
Student ID: {student_id}
Class: {row['class']}
Maths: {row['maths']}
Science: {row['science']}
English: {row['english']}
Total Marks: {row['total']}
"""

    collection.add(
        documents=[attendance_text],
        ids=[f"attendance_{student_id}"],
        metadatas=[{"type": "attendance", "student_id": str(student_id)}],
    )
    collection.add(
        documents=[fees_text],
        ids=[f"fees_{student_id}"],
        metadatas=[{"type": "fees", "student_id": str(student_id)}],
    )
    collection.add(
        documents=[marks_text],
        ids=[f"marks_{student_id}"],
        metadatas=[{"type": "marks", "student_id": str(student_id)}],
    )

conn.close()

print("All data loaded successfully!")
print("Total records:", collection.count())
