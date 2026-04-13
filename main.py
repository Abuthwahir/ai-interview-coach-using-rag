import argparse

from interview_coach import InterviewCoach


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run the AI Interview Coach CLI.")
    parser.add_argument(
        "--job",
        default=None,
        help="Optional path to a .txt job description file for RAG-based questions."
    )
    parser.add_argument(
        "--questions",
        type=int,
        default=None,
        help="Maximum number of interview questions."
    )
    parser.add_argument(
        "--level",
        default=None,
        help="Candidate level such as junior, mid, or senior."
    )
    parser.add_argument(
        "--position",
        default=None,
        help="Target position, for example Python Developer."
    )
    parser.add_argument(
        "--type",
        dest="interview_type",
        default=None,
        help="Interview type such as technical, behavioral, or system design."
    )
    parser.add_argument(
        "--focus-area",
        default=None,
        help="Primary focus area for the interview."
    )
    return parser


def print_feedback(evaluation):
    print("\nFeedback")
    print("-" * 40)
    print(f"Score: {evaluation['score']}/10")
    print(f"Strengths: {evaluation['strengths']}")
    print(f"Improvements: {evaluation['improvements']}")
    print(f"Correct Answer: {evaluation['correct_answer']}")


def print_report(report):
    print("\nFinal Report")
    print("=" * 50)
    print(f"Position: {report['position']}")
    print(f"Level: {report['level']}")
    print(f"Interview Type: {report['interview_type']}")
    print(f"Focus Area: {report['focus_area']}")
    print(f"RAG Enabled: {'Yes' if report['rag_enabled'] else 'No'}")
    print(f"Questions Completed: {report['questions_completed']}/{report['max_questions']}")
    print(f"Average Score: {report['average_score']}/10")
    print(f"Overall Assessment: {report['overall_assessment']}")

    if report["strengths_summary"]:
        print("\nTop Strengths:")
        for item in report["strengths_summary"]:
            print(f"- {item}")

    if report["improvements_summary"]:
        print("\nTop Improvements:")
        for item in report["improvements_summary"]:
            print(f"- {item}")

    if report["rounds"]:
        print("\nPer Question Summary:")
        for item in report["rounds"]:
            print("-" * 40)
            print(f"Q{item['question_number']}: {item['question']}")
            print(f"Answer: {item['answer']}")
            print(f"Score: {item['score']}/10")
            print(f"Topic: {item['topic']} | Difficulty: {item['difficulty']}")


def run_cli():
    args = build_parser().parse_args()

    coach = InterviewCoach(
        position=args.position,
        level=args.level,
        interview_type=args.interview_type,
        focus_area=args.focus_area,
        max_questions=args.questions,
        job_description_path=args.job
    )

    opening = coach.start_interview()

    print("=" * 50)
    print("AI Interview Coach")
    print("=" * 50)
    print(f"Position: {coach.position}")
    print(f"Level: {coach.level}")
    print(f"Interview Type: {coach.interview_type}")
    print(f"RAG Enabled: {'Yes' if coach.rag_enabled else 'No'}")
    print("Type 'quit' to stop early.\n")

    print(f"Question {opening['question_number']}: {opening['question']}\n")

    while not coach.completed:
        answer = input("Your answer: ").strip()

        if not answer:
            print("Please enter an answer before continuing.\n")
            continue

        if answer.lower() in {"quit", "exit"}:
            break

        result = coach.submit_answer(answer)
        print_feedback(result["evaluation"])

        if result["interview_complete"]:
            break

        print(f"\nQuestion {result['question_number']}: {result['next_question']}\n")

    print_report(coach.generate_report())


if __name__ == "__main__":
    run_cli()
