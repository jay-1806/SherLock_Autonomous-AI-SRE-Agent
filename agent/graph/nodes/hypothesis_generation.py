"""Step 3: GPT-4o hypothesis generation."""

import json
import os
import time

from agent.graph.state import InvestigationState
from agent.llm.client import chat_completion
from agent.models.hypothesis import Hypothesis
from agent.prompts.hypothesis_generation import SYSTEM_PROMPT, build_user_prompt


async def generate_hypotheses(state: InvestigationState) -> dict:
    start = time.time()

    user_prompt = build_user_prompt(
        alert=state["alert"],
        service_context=state.get("affected_service_context"),
        recent_deployments=state.get("deployment_history"),
        similar_incidents=state.get("similar_incidents"),
    )

    try:
        content = await chat_completion(
            model=os.environ.get("OPENAI_REASONING_MODEL", "gpt-4o"),
            temperature=float(os.environ.get("OPENAI_REASONING_TEMPERATURE", "0.1")),
            max_tokens=2000,
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
        )
        raw = json.loads(content)
        hypotheses = [Hypothesis(**h) for h in raw.get("hypotheses", [])]
    except Exception:
        hypotheses = []

    return {
        "hypotheses": hypotheses,
        "step_timings": {
            **state.get("step_timings", {}),
            "generate_hypotheses": time.time() - start,
        },
    }
