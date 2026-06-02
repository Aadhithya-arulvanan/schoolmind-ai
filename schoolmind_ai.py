import google.generativeai as genai

from chroma_tools import get_student_records
from translator import detect_language
from report_generator import generate_report

from analytics import (
    get_all_marks,
    get_all_fees,
    get_all_attendance,
    get_at_risk_students
)

from local_intent import classify_intent
from local_name import extract_name


import os

genai.configure(
    api_key=os.getenv(
        "GEMINI_API_KEY"
    )
)

model = genai.GenerativeModel(
    "gemini-3.1-flash-lite"
)


def ask_schoolmind(question):

    language = detect_language(
        question
    )

    intent = classify_intent(
        question
    )

    # MARKS QUESTIONS
    if intent == "marks_query":

        context = get_all_marks().to_string(
            index=False
        )

    # FEES QUESTIONS
    elif intent == "fees_query":

        context = get_all_fees().to_string(
            index=False
        )

    # ATTENDANCE QUESTIONS
    elif intent == "attendance_query":

        context = get_all_attendance().to_string(
            index=False
        )

    # RISK ANALYSIS
    elif intent == "risk_analysis":

        students = get_at_risk_students()

        if students.empty:

            return "No at-risk students found."

        answer = (
            "🚨 At-Risk Students\n\n"
            "Criteria:\n"
            "- Attendance below 75%\n"
            "- OR Pending Fee above ₹25,000\n"
            "- OR Total Marks below 220\n\n"
        )

        for _, row in students.iterrows():

            answer += (
                f"Name: {row['Name']}\n"
                f"Attendance: {row['AttendancePercent']}%\n"
                f"Pending Fee: ₹{row['PendingFee']}\n"
                f"Total Marks: {row['Total']}\n\n"
            )

        return answer
    # PDF REPORT GENERATION
    elif intent == "student_report":

        student_name = extract_name(
            question
        )

        if not student_name:

            return "Student name not found."

        records = get_student_records(
            student_name
        )

        context = "\n".join(
            records
        )

        report_language = (
            language if language else "English"
        )

        prompt = f"""
Create a professional student report.

Language: {report_language}

Student Data:

{context}

Include:

1. Student Profile
2. Academic Performance
3. Attendance
4. Financial Status
5. Overall Assessment
"""

        report_text = model.generate_content(
            prompt
        ).text

        pdf_file = generate_report(
            student_name,
            report_text
        )

        
        return pdf_file

    # STUDENT SUMMARY
    elif intent == "student_summary":

        student_name = extract_name(
            question
        )

        if not student_name:

            return "Student name not found."

        records = get_student_records(
            student_name
        )

        context = "\n".join(
            records
        )

        summary_language = (
            language if language else "English"
        )

        summary_prompt = f"""
Create a professional student summary.

Language: {summary_language}

Student Data:

{context}

Include:

1. Student Profile
2. Academic Performance
3. Attendance
4. Financial Status
5. Overall Assessment
"""

        response = model.generate_content(
            summary_prompt
        )

        return response.text

    else:

        return (
            "Sorry, I could not understand "
            "the question."
        )

    answer_prompt = f"""
You are SchoolMind AI.

Question:
{question}

Data:
{context}

Rules:

1. Use ONLY the provided data.
2. Do not make up information.
3. If asked for highest, find highest.
4. If asked for lowest, find lowest.
5. If asked for rankings, rank students.
6. Be concise and accurate.
"""

    print("\nINTENT:", intent)
    print("\nCONTEXT:\n")
    print(context)

    response = model.generate_content(
        answer_prompt
    )

    answer = response.text

    if language:

        translation_prompt = f"""
You are a professional translator.

Translate EVERYTHING below into {language}.

Rules:
- Translate the complete text.
- Do not leave any English words.
- Do not add explanations.
- Do not add introductions.
- Do not ask questions.
- Return only the translated text.

TEXT:

{answer}
"""

        answer = model.generate_content(
            translation_prompt
        ).text

    return answer
