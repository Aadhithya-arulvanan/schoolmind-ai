import pandas as pd
import chromadb

client = chromadb.PersistentClient(
    path="./chroma_db"
)

collection = client.get_or_create_collection(
    name="students"
)

df = pd.read_csv("data/attendance.csv")

for _, row in df.iterrows():

    text = f"""
Student Name: {row['Name']}
Student ID: {row['StudentID']}
Class: {row['Class']}
Attendance Percentage: {row['AttendancePercent']}
Days Present: {row['DaysPresent']}
Days Absent: {row['DaysAbsent']}
"""

    collection.add(
        documents=[text],
        ids=[str(row["StudentID"])]
    )

print("All students stored in ChromaDB")