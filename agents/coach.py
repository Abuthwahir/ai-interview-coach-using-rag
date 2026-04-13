from typing import Dict, List, Optional

from agents.tools import (
    get_easy_question,
    get_medium_question,
    get_hard_question,
    evaluate_answer,
    set_difficulty,
    reset_interview_state
)


DEFAULT_TOPICS = [
    "python basics",
    "data structures",
    "oops",
    "async programming",
    "web frameworks"
]


class AdaptiveInterviewFlow:
    """Structured adaptive flow that keeps the original function-based logic."""

    def __init__(self, topic: str = "python basics", topics: Optional[List[str]] = None):
        source_topics = topics or DEFAULT_TOPICS
        self.topics = self._build_topics(topic, source_topics)
        self.topic_index = self._resolve_topic_index(topic)
        self.last_question = ""
        self.scores = []

        reset_interview_state()
        set_difficulty.invoke({"level": "medium"})

    def _build_topics(self, topic: str, source_topics: List[str]) -> List[str]:
        topics = []
        normalized_topic = (topic or "").strip().lower()

        if normalized_topic:
            topics.append(normalized_topic)

        for item in source_topics:
            normalized_item = (item or "").strip().lower()
            if normalized_item and normalized_item not in topics:
                topics.append(normalized_item)

        return topics or DEFAULT_TOPICS[:]

    def _resolve_topic_index(self, topic: str) -> int:
        normalized_topic = (topic or "").strip().lower()
        if normalized_topic in self.topics:
            return self.topics.index(normalized_topic)
        return 0

    @staticmethod
    def score_to_level(score: int) -> str:
        if score >= 8:
            return "hard"
        if score >= 5:
            return "medium"
        return "easy"

    def current_topic(self) -> str:
        return self.topics[self.topic_index]

    def build_question(self, level: str, topic: Optional[str] = None) -> str:
        current_topic = topic or self.current_topic()

        if level == "easy":
            question = get_easy_question.invoke({"topic": current_topic})
        elif level == "hard":
            question = get_hard_question.invoke({"topic": current_topic})
        else:
            question = get_medium_question.invoke({"topic": current_topic})

        if question == self.last_question:
            question = f"{question} (follow-up: include one concrete example)"

        self.last_question = question
        return question

    def start_plan(self, initial_level: str = "medium") -> Dict[str, str]:
        set_difficulty.invoke({"level": initial_level})
        return {
            "level": initial_level,
            "topic": self.current_topic()
        }

    def plan_next_step(
        self,
        answer: str = "",
        score: Optional[int] = None,
    ) -> Dict[str, object]:
        if score is None:
            eval_result = evaluate_answer.invoke({"answer": answer})
            score = int(eval_result["score"])

        self.scores.append(score)
        avg_score = sum(self.scores) / len(self.scores)
        level = self.score_to_level(score)

        set_difficulty.invoke({"level": level})

        if score >= 5:
            self.topic_index = (self.topic_index + 1) % len(self.topics)

        return {
            "score": score,
            "avg_score": avg_score,
            "level": level,
            "topic": self.current_topic()
        }

    def start(self, initial_level: str = "medium") -> Dict[str, object]:
        plan = self.start_plan(initial_level=initial_level)
        plan["question"] = self.build_question(plan["level"], plan["topic"])
        return plan

    def step(self, answer: str) -> Dict[str, object]:
        plan = self.plan_next_step(answer=answer)
        plan["question"] = self.build_question(plan["level"], plan["topic"])
        return plan


def create_interview_agent(topic: str = "python basics"):
    """Return a pure Python step function for adaptive interviewing."""
    flow = AdaptiveInterviewFlow(topic=topic)

    def agent_step(answer: str) -> str:
        result = flow.step(answer)

        return (
            f"Score this round: {result['score']}/10 | "
            f"Average: {result['avg_score']:.1f}/10\n"
            f"Next question ({result['level']}): {result['question']}"
        )

    return agent_step
