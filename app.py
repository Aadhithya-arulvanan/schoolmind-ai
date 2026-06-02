import streamlit as st

from schoolmind_ai import ask_schoolmind
st.title("🎓 SchoolMind AI")
from analytics import get_dashboard_stats

stats = get_dashboard_stats()


st.sidebar.metric(
    "Students",
    stats["total_students"]
)

st.sidebar.metric(
    "Average Attendance",
    f"{stats['avg_attendance']}%"
)

st.sidebar.metric(
    "Pending Fees",
    f"₹{stats['total_pending_fees']}"
)

st.sidebar.metric(
    "Top Marks",
    f"{stats['top_marks']}"
)


question = st.text_input(
    "Ask a question"
)

if question:

    try:

        answer = ask_schoolmind(
            question
        )

        st.subheader("Answer")

        st.success(answer)

    except Exception as e:

        st.error(
            f"Error: {str(e)}"
        )