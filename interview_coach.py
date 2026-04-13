from pathlib import Path
from typing import Dict, List, Optional

from agents.coach import AdaptiveInterviewFlow
from chains.evaluator import create_evaluator_chain, parser
from chains.interviewer import create_interviewer_chain_with_memory
from config import get_settings
from memory.conversation import create_memory
from rag.setup import setup_interview_rag


class InterviewCoach:
    """Central application service for running interview sessions."""

    def __init__(
        self,
        position: Optional[str] = None,
        level: Optional[str] = None,
        interview_type: Optional[str] = None,
        focus_area: Optional[str] = None,
        max_questions: Optional[int] = None,
        job_description_path: Optional[str] = None,
    ):
        self.settings = get_settings()
        self.position = position or self.settings.default_position
        self.level = level or self.settings.default_level
        self.interview_type = interview_type or self.settings.default_interview_type
        self.focus_area = focus_area or self.settings.default_focus_area
        self.max_questions = max_questions or self.settings.max_questions

        self.memory = create_memory()
        self.interviewer = create_interviewer_chain_with_memory(
            self.memory,
            model_name=self.settings.model_name,
            temperature=self.settings.temperature,
            api_key=self.settings.groq_api_key
        )
        self.evaluator = create_evaluator_chain(
            model_name=self.settings.model_name,
            temperature=self.settings.evaluator_temperature,
            api_key=self.settings.groq_api_key
        )

        self.job_description_path = self._resolve_job_description(job_description_path)
        self.rag_enabled = self.job_description_path is not None
        self.question_generator = None
        if self.rag_enabled:
            self.question_generator = setup_interview_rag(
                self.job_description_path,
                model_name=self.settings.model_name,
                temperature=self.settings.temperature,
                api_key=self.settings.groq_api_key
            )

        self.adaptive_flow = AdaptiveInterviewFlow(
            topic=self.focus_area,
            topics=self._build_topics(self.focus_area)
        )

        self.questions: List[str] = []
        self.answers: List[str] = []
        self.scores: List[int] = []
        self.feedback_log: List[Dict[str, object]] = []
        self.rounds: List[Dict[str, object]] = []
        self.transcript: List[Dict[str, object]] = []

        self.current_question: Optional[str] = None
        self.current_topic: Optional[str] = None
        self.current_difficulty: Optional[str] = None
        self.started = False
        self.completed = False

    def start_interview(self) -> Dict[str, object]:
        if self.started and self.current_question:
            return {
                "question_number": len(self.questions),
                "question": self.current_question,
                "topic": self.current_topic,
                "difficulty": self.current_difficulty,
                "rag_enabled": self.rag_enabled
            }

        plan = self.adaptive_flow.start_plan(initial_level=self._initial_difficulty())
        question = self._generate_question(
            topic=plan["topic"],
            difficulty=plan["level"],
            is_first_question=True
        )

        self.started = True
        return {
            "question_number": len(self.questions),
            "question": question,
            "topic": self.current_topic,
            "difficulty": self.current_difficulty,
            "rag_enabled": self.rag_enabled
        }

    def submit_answer(self, answer: str) -> Dict[str, object]:
        if not self.started:
            self.start_interview()

        if self.completed:
            raise RuntimeError("Interview is already complete.")

        answer_text = (answer or "").strip()
        if not answer_text:
            raise ValueError("Answer cannot be empty.")

        current_question = self.current_question or ""
        current_topic = self.current_topic or self.focus_area
        current_difficulty = self.current_difficulty or "medium"

        self.answers.append(answer_text)
        self.memory.chat_memory.add_user_message(answer_text)
        self.transcript.append({
            "role": "user",
            "kind": "answer",
            "content": answer_text
        })

        evaluation = self._evaluate_answer(current_question, answer_text)
        score = int(evaluation["score"])

        self.scores.append(score)
        self.feedback_log.append(evaluation)
        self.rounds.append({
            "question_number": len(self.answers),
            "question": current_question,
            "answer": answer_text,
            "score": score,
            "strengths": evaluation["strengths"],
            "improvements": evaluation["improvements"],
            "correct_answer": evaluation["correct_answer"],
            "topic": current_topic,
            "difficulty": current_difficulty
        })
        self.transcript.append({
            "role": "assistant",
            "kind": "feedback",
            "content": self._feedback_text(evaluation),
            "score": score
        })

        if len(self.answers) >= self.max_questions:
            self.completed = True
            return {
                "evaluation": evaluation,
                "next_question": None,
                "question_number": len(self.questions),
                "interview_complete": True,
                "report": self.generate_report()
            }

        plan = self.adaptive_flow.plan_next_step(score=score)
        next_question = self._generate_question(
            topic=plan["topic"],
            difficulty=plan["level"],
            is_first_question=False
        )

        return {
            "evaluation": evaluation,
            "next_question": next_question,
            "question_number": len(self.questions),
            "topic": self.current_topic,
            "difficulty": self.current_difficulty,
            "remaining_questions": self.max_questions - len(self.answers),
            "interview_complete": False
        }

    def generate_report(self) -> Dict[str, object]:
        average_score = round(sum(self.scores) / len(self.scores), 2) if self.scores else 0.0

        return {
            "position": self.position,
            "level": self.level,
            "interview_type": self.interview_type,
            "focus_area": self.focus_area,
            "job_description": self.job_description_path,
            "rag_enabled": self.rag_enabled,
            "questions_completed": len(self.rounds),
            "max_questions": self.max_questions,
            "average_score": average_score,
            "overall_assessment": self._overall_assessment(average_score),
            "strengths_summary": self._collect_unique_feedback("strengths"),
            "improvements_summary": self._collect_unique_feedback("improvements"),
            "rounds": self.rounds,
            "transcript": self._transcript_text()
        }

    def _resolve_job_description(self, job_description_path: Optional[str]) -> Optional[str]:
        if not job_description_path:
            return None

        path = Path(job_description_path)
        if path.exists() and path.is_file():
            return str(path)
        return None

    def _build_topics(self, focus_area: str) -> List[str]:
        default_topics = [
            "python basics",
            "data structures",
            "oops",
            "async programming",
            "web frameworks"
        ]
        normalized_focus = (focus_area or "").strip().lower()
        if normalized_focus and normalized_focus not in default_topics:
            return [normalized_focus] + default_topics
        return default_topics

    def _initial_difficulty(self) -> str:
        level_map = {
            "junior": "easy",
            "entry": "easy",
            "mid": "medium",
            "middle": "medium",
            "senior": "hard",
            "lead": "hard",
            "staff": "hard"
        }
        return level_map.get((self.level or "").strip().lower(), "medium")

    def _draft_question(self, topic: str, difficulty: str) -> str:
        fallback_question = self.adaptive_flow.build_question(difficulty, topic)

        if not self.question_generator:
            return fallback_question

        try:
            return self.question_generator.invoke({
                "topic": topic,
                "difficulty": difficulty,
                "previous_questions": ", ".join(self.questions) if self.questions else "None"
            })
        except Exception:
            return fallback_question

    def _generate_question(
        self,
        topic: str,
        difficulty: str,
        is_first_question: bool,
    ) -> str:
        draft_question = self._draft_question(topic, difficulty)

        if is_first_question:
            instruction = (
                f"Start the interview for a {self.position} role. "
                f"Ask one {difficulty} level question about {topic}. "
                f"Use this draft question as the core idea: {draft_question}. "
                "Ask only the final question."
            )
        else:
            instruction = (
                f"Ask the next {difficulty} level interview question about {topic}. "
                f"Use this draft question as the core idea: {draft_question}. "
                "Avoid repeating previous questions and ask only one question."
            )

        try:
            question = self.interviewer.invoke({
                "interview_type": self.interview_type,
                "level": self.level,
                "focus_area": self.focus_area,
                "input": instruction
            })
        except Exception:
            question = draft_question

        self.current_question = question.strip()
        self.current_topic = topic
        self.current_difficulty = difficulty
        self.questions.append(self.current_question)
        self.memory.chat_memory.add_ai_message(self.current_question)
        self.transcript.append({
            "role": "assistant",
            "kind": "question",
            "content": self.current_question
        })

        return self.current_question

    def _evaluate_answer(self, question: str, answer: str) -> Dict[str, object]:
        try:
            evaluation = self.evaluator.invoke({
                "question": question,
                "answer": answer,
                "format_instructions": parser.get_format_instructions()
            })
        except Exception:
            evaluation = self._fallback_evaluation(answer)

        evaluation["score"] = self._normalize_score(evaluation.get("score", 0))
        evaluation["strengths"] = str(
            evaluation.get("strengths", "Clear attempt to answer the question.")
        )
        evaluation["improvements"] = str(
            evaluation.get("improvements", "Add more detail, examples, and technical reasoning.")
        )
        evaluation["correct_answer"] = str(
            evaluation.get(
                "correct_answer",
                "Provide a more structured explanation with a real example."
            )
        )
        return evaluation

    def _fallback_evaluation(self, answer: str) -> Dict[str, object]:
        word_count = len(answer.split())

        if word_count < 10:
            score = 3
        elif word_count < 30:
            score = 5
        elif word_count < 60:
            score = 7
        else:
            score = 9

        return {
            "score": score,
            "strengths": "You addressed the question directly.",
            "improvements": "Expand the answer with more depth, structure, and one concrete example.",
            "correct_answer": "A strong answer should define the concept, explain why it matters, and include a practical example."
        }

    def _normalize_score(self, score: object) -> int:
        try:
            numeric_score = int(score)
        except (TypeError, ValueError):
            numeric_score = 0
        return max(0, min(10, numeric_score))

    def _feedback_text(self, evaluation: Dict[str, object]) -> str:
        return (
            f"Score: {evaluation['score']}/10\n"
            f"Strengths: {evaluation['strengths']}\n"
            f"Improvements: {evaluation['improvements']}\n"
            f"Correct answer: {evaluation['correct_answer']}"
        )

    def _collect_unique_feedback(self, key: str) -> List[str]:
        values = []
        for item in self.feedback_log:
            text = str(item.get(key, "")).strip()
            if text and text not in values:
                values.append(text)
            if len(values) == 3:
                break
        return values

    def _overall_assessment(self, average_score: float) -> str:
        if average_score >= 8:
            return "Strong performance"
        if average_score >= 6:
            return "Good performance with a few gaps"
        if average_score > 0:
            return "Needs more practice"
        return "No answers submitted yet"

    def _transcript_text(self) -> str:
        lines = []
        for entry in self.transcript:
            if entry["kind"] == "question":
                lines.append(f"Interviewer: {entry['content']}")
            elif entry["kind"] == "answer":
                lines.append(f"Candidate: {entry['content']}")
        return "\n".join(lines)
