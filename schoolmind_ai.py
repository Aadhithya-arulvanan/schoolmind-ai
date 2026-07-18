import google.generativeai as genai

from chroma_tools import get_student_records
from translator import detect_language
from report_generator import generate_report

from analytics import (
    get_all_marks,
    get_all_fees,
    get_all_attendance,
    get_at_risk_students,
    query_marks,
    query_fees,
    query_attendance,
)

from local_intent import classify_intent
from local_name import extract_name


import os

genai.configure(
    api_key=
        "GEMINI_API_KEY"
    
)

model = genai.GenerativeModel(
    "gemini-3.1-flash-lite"
)

def parse_query_intent(question):
    q = question.lower()
    ascending = any(w in q for w in ["lowest", "least", "worst", "minimum"])
    wants_ranked = ascending or any(w in q for w in ["highest", "top", "best", "maximum"])
    limit = 1
    for word in q.split():
        if word.isdigit():
            limit = int(word)
    name = extract_name(question)
    return {"ranked": wants_ranked, "ascending": ascending, "limit": limit, "name": name}

def ask_schoolmind(question):

    language = detect_language(
        question
    )

    intent = classify_intent(
        question
    )

    # MARKS QUESTIONS
    if intent in ("marks_query", "fees_query", "attendance_query"):
        q_info = parse_query_intent(question)
        query_fn = {"marks_query": query_marks, "fees_query": query_fees, "attendance_query": query_attendance}[intent]

        if q_info["name"]:
            result_df = query_fn(name=q_info["name"])
        elif q_info["ranked"]:
            result_df = query_fn(ascending=q_info["ascending"], limit=q_info["limit"])
        else:
            result_df = query_fn()  # fallback: full table, only for genuinely open-ended questions

        context = result_df.to_string(index=False)

    # RISK ANALYSIS
    elif intent == "risk_analysis":

        students = get_at_risk_students()

        if students.empty:

            return "No at-risk students found."

        answer = (
            "🚨 At-Risk Students\n\n"
            "Criteria:\n"
            "- Attendance below 75%\n"
            "- OR Pending Fee above ₹30,000\n"
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
Create a professional student report using ONLY the data provided below.

Language: {report_language}

Student Data:
{context}

Rules:
- If "Student Data" above is empty or does not contain attendance, fee, or
  marks information, do NOT generate a report. Instead respond only with:
  "No records were found for this student — a report cannot be generated."
- Do not invent, estimate, or infer any number, grade, or attendance figure
  that is not explicitly present in the data above.
- If one category (e.g. Financial Status) is missing from the data but
  others are present, state "Data not available" for that section rather
  than guessing.

Include (only using sections supported by the data):
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
Create a professional student summary using ONLY the data provided below.

Language: {summary_language}

Student Data:
{context}

Rules:
- If "Student Data" above is empty or does not contain attendance, fee, or
  marks information, do NOT generate a summary. Instead respond only with:
  "No records were found for this student — a summary cannot be generated."
- Do not invent, estimate, or infer any number, grade, or attendance figure
  that is not explicitly present in the data above.
- If one category (e.g. Financial Status) is missing from the data but
  others are present, state "Data not available" for that section rather
  than guessing.

Include (only using sections supported by the data):
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
You are SchoolMind AI, a school data assistant.

Question:
{question}

Data (already filtered/sorted to answer this exact question — do not re-rank or recompute):
{context}

Rules:
1. Use ONLY the rows in "Data" above. Never use outside knowledge about
   students, schools, or typical academic performance.
2. Do not perform any additional ranking, sorting, or filtering — the data
   given is already the answer set.
3. If "Data" is empty or contains no rows, respond exactly with:
   "I couldn't find any records matching that question."
   Do not guess a plausible-sounding name or number.
4. State the answer in one or two plain sentences. Include the exact
   figure(s) from the data (do not round or approximate).
5. Do not mention SQL, databases, or how the data was retrieved.
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
