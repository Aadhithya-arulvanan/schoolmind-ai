
import os


if not os.path.exists("schoolmind.db"):
    from db import migrate_csv_to_sqlite
    migrate_csv_to_sqlite()

if not os.path.exists("chroma_db"):
    import load_all_data

import streamlit as st
from auth import check_login
from schoolmind_ai import ask_schoolmind
from analytics import get_dashboard_stats
from local_intent import classify_intent
from local_name import extract_name

st.title("🎓 SchoolMind AI")

# ---------- LOGIN GATE ----------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.subheader("Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        user = check_login(username, password)
        if user:
            st.session_state.logged_in = True
            st.session_state.username = username
            st.session_state.role = user["role"]
            st.session_state.student_name = user.get("student_name")
            st.rerun()
        else:
            st.error("Invalid username or password.")

    st.stop()

# ---------- LOGGED IN VIEW ----------
st.sidebar.success(f"Logged in as {st.session_state.username} ({st.session_state.role})")

if st.sidebar.button("Logout"):
    for key in ["logged_in", "username", "role", "student_name"]:
        st.session_state.pop(key, None)
    st.rerun()

# Principal/Teacher see school-wide stats; Parent only sees their own child
if st.session_state.role in ("Principal", "Teacher"):
    stats = get_dashboard_stats()
    st.sidebar.metric("Students", stats["total_students"])
    st.sidebar.metric("Average Attendance", f"{stats['avg_attendance']}%")
    st.sidebar.metric("Pending Fees", f"₹{stats['total_pending_fees']}")
    st.sidebar.metric("Top Marks", f"{stats['top_marks']}")
else:
    st.sidebar.info(f"Viewing data for: {st.session_state.student_name}")

question = st.text_input("Ask a question")

if question:
    try:
        # ---------- ROLE-BASED ACCESS CONTROL ----------
        if st.session_state.role == "Parent":
            intent = classify_intent(question)
            name_in_question = extract_name(question)

            allowed_intents = (
                "student_summary",
                "student_report",
                "marks_query",
                "attendance_query",
                "fees_query",
            )
            if intent not in allowed_intents:
                st.error("Parents can only ask about their child's marks, attendance, fees, or ask for a summary/report.")
                st.stop()

            if name_in_question and name_in_question != st.session_state.student_name:
                st.error("Parents can only view their own child's information.")
                st.stop()

            # Force the question to be scoped to their own child
            question = f"{question} {st.session_state.student_name}"

        answer = ask_schoolmind(question)
        st.subheader("Answer")

        # PDF report handling
        if (
            isinstance(answer, str)
            and answer.endswith(".pdf")
            and os.path.exists(answer)
        ):
            st.success(f"PDF Report Generated: {answer}")
            with open(answer, "rb") as pdf_file:
                st.download_button(
                    label="📄 Download Report",
                    data=pdf_file,
                    file_name=answer,
                    mime="application/pdf",
                )
        else:
            st.success(answer)

    except Exception as e:
        st.error(f"Error: {str(e)}")