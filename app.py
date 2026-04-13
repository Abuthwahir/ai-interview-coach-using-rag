from pathlib import Path

import streamlit as st

from interview_coach import InterviewCoach


def available_job_descriptions():
    data_dir = Path("data/job_descriptions")
    if not data_dir.exists():
        return []
    return [str(path) for path in sorted(data_dir.glob("*.txt"))]


def start_session(position, level, interview_type, focus_area, question_count, job_path):
    coach = InterviewCoach(
        position=position,
        level=level,
        interview_type=interview_type,
        focus_area=focus_area,
        max_questions=question_count,
        job_description_path=job_path
    )
    coach.start_interview()
    st.session_state.coach = coach
    st.session_state.report = None


def reset_session():
    for key in ["coach", "report"]:
        if key in st.session_state:
            del st.session_state[key]


st.set_page_config(page_title="AI Interview Coach", layout="wide")
st.title("AI Interview Coach")
st.caption("Answer each question, review feedback, and finish with a full interview report.")

job_options = ["None"] + available_job_descriptions()

with st.sidebar:
    st.header("Interview Setup")
    position = st.text_input("Position", value="Python Developer")
    level = st.selectbox("Level", ["junior", "mid", "senior"], index=1)
    interview_type = st.selectbox(
        "Interview type",
        ["technical", "behavioral", "system design", "mixed"],
        index=0
    )
    focus_area = st.text_input("Focus area", value="Python fundamentals")
    question_count = st.number_input("Questions", min_value=1, max_value=15, value=5, step=1)
    selected_job = st.selectbox("Job description", job_options, index=0)
    custom_job_path = st.text_input("Custom job description path", value="")

    job_path = custom_job_path.strip() or (None if selected_job == "None" else selected_job)

    if st.button("Start Interview", use_container_width=True):
        start_session(
            position=position,
            level=level,
            interview_type=interview_type,
            focus_area=focus_area,
            question_count=int(question_count),
            job_path=job_path
        )
        st.rerun()

    if st.button("Reset", use_container_width=True):
        reset_session()
        st.rerun()


coach = st.session_state.get("coach")

if not coach:
    st.info("Configure the interview in the sidebar and click Start Interview.")
else:
    status_col, score_col, rag_col = st.columns(3)
    status_col.metric("Questions Asked", len(coach.questions))
    score_col.metric(
        "Average Score",
        f"{(sum(coach.scores) / len(coach.scores)):.1f}/10" if coach.scores else "0.0/10"
    )
    rag_col.metric("RAG Mode", "On" if coach.rag_enabled else "Off")

    for entry in coach.transcript:
        role = "assistant" if entry["role"] == "assistant" else "user"
        with st.chat_message(role):
            if entry["kind"] == "feedback":
                st.markdown("**Feedback**")
            st.write(entry["content"])

    if not coach.completed:
        answer = st.chat_input("Write your answer here")
        if answer:
            result = coach.submit_answer(answer)
            if result["interview_complete"]:
                st.session_state.report = result["report"]
            st.rerun()

    report = st.session_state.get("report")
    if coach.completed and not report:
        report = coach.generate_report()
        st.session_state.report = report

    if report:
        st.subheader("Final Report")
        summary_col, completed_col = st.columns(2)
        summary_col.metric("Average Score", f"{report['average_score']}/10")
        completed_col.metric(
            "Completed",
            f"{report['questions_completed']}/{report['max_questions']}"
        )
        st.write(report["overall_assessment"])

        if report["strengths_summary"]:
            st.markdown("**Strengths**")
            for item in report["strengths_summary"]:
                st.write(f"- {item}")

        if report["improvements_summary"]:
            st.markdown("**Improvements**")
            for item in report["improvements_summary"]:
                st.write(f"- {item}")

        for item in report["rounds"]:
            with st.expander(f"Question {item['question_number']} | Score {item['score']}/10"):
                st.write(f"**Question:** {item['question']}")
                st.write(f"**Answer:** {item['answer']}")
                st.write(f"**Strengths:** {item['strengths']}")
                st.write(f"**Improvements:** {item['improvements']}")
                st.write(f"**Correct Answer:** {item['correct_answer']}")
