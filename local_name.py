from db import get_connection


def extract_name(question):

    q = question.lower()

    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT name FROM students")
    names = [row["name"] for row in cur.fetchall()]
    conn.close()

    for name in names:

        if name.lower() in q:

            return name

    return None