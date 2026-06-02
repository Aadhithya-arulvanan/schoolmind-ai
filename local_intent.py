def classify_intent(question):

    q = question.lower()
    words = set(q.split())

    # Reports
    if {"report", "pdf"} & words:
        return "student_report"

    # Student summary
    elif (
        "tell about" in q
        or "profile" in words
        or "summary" in words
    ):
        return "student_summary"

    # Attendance
    elif (
        "attendance" in words
        or "present" in words
        or "absent" in words
    ):
        return "attendance_query"

    # Fees
    elif (
        "fee" in words
        or "fees" in words
        or "money" in words
        or "owes" in words
        or "payment" in words
    ):
        return "fees_query"

    # Risk
    elif (
        "risk" in words
        or "attention" in words
        or "intervention" in words
    ):
        return "risk_analysis"

    # Marks
    elif (
        "mark" in words
        or "marks" in words
        or "score" in words
        or "scored" in words
        or "topper" in words
        or "rank" in words
        or "highest" in words
        or "lowest" in words
    ):
        return "marks_query"

    return "unknown"