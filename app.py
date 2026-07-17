import os


if not os.path.exists("schoolmind.db"):
    from db import migrate_csv_to_sqlite
    migrate_csv_to_sqlite()

if not os.path.exists("chroma_db"):
    import load_all_data

import streamlit as st
from schoolmind_ai import ask_schoolmind
from analytics import get_dashboard_stats

st.title("🎓 SchoolMind AI")

stats = get_dashboard_stats()

st.sidebar.metric("Students", stats["total_students"])
st.sidebar.metric("Average Attendance", f"{stats['avg_attendance']}%")
st.sidebar.metric("Pending Fees", f"₹{stats['total_pending_fees']}")
st.sidebar.metric("Top Marks", f"{stats['top_marks']}")

question = st.text_input("Ask a question")

if question:
    try:
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
