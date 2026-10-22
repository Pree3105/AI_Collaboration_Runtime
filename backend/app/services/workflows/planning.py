import json
import logging

from openai import APITimeoutError, OpenAI
from pydantic import ValidationError as PydanticValidationError

from app.config import settings
from app.database import get_redis_client
from app.exceptions import PlanningError
from app.schemas import ExecutionPlan

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = (
    "You are an expert task planner. Given a task description, break it down "
    "into a JSON execution plan with fields: task_id (int), steps (list of "
    "objects with step_id, name, description, depends_on, requires_decision), "
    "and summary (string). Respond with JSON only."
)

CACHE_TTL_SECONDS = 300


def _cache_key(task_id: int) -> str:
    return f"plan:{task_id}:v1"


def _fallback_plan(task_id: int, task_description: str) -> ExecutionPlan:
    return ExecutionPlan(
        task_id=task_id,
        steps=[
            {
                "step_id": "step-1",
                "name": "Manual review required",
                "description": f"Automated planning failed; review manually: {task_description}",
                "depends_on": [],
                "requires_decision": True,
            }
        ],
        summary="Fallback plan (planning service unavailable).",
    )


class PlanningService:
    def __init__(self) -> None:
        self.client = OpenAI(api_key=settings.openai_api_key)
        self.redis = get_redis_client()

    async def generate_plan(self, task_description: str, task_id: int) -> ExecutionPlan:
        cache_key = _cache_key(task_id)

        cached = self.redis.get(cache_key)
        if cached:
            logger.info("planning cache hit for task_id=%s", task_id)
            return ExecutionPlan.model_validate_json(cached)

        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": task_description},
                ],
                max_tokens=1000,
                timeout=30,
                response_format={"type": "json_object"},
            )
        except APITimeoutError:
            logger.error("OpenAI request timed out for task_id=%s", task_id)
            return _fallback_plan(task_id, task_description)
        except Exception:
            logger.exception("OpenAI request failed for task_id=%s", task_id)
            return _fallback_plan(task_id, task_description)

        usage = response.usage
        if usage:
            logger.info(
                "OpenAI usage task_id=%s prompt_tokens=%s completion_tokens=%s",
                task_id,
                usage.prompt_tokens,
                usage.completion_tokens,
            )

        raw_content = response.choices[0].message.content or ""
        try:
            plan_data = json.loads(raw_content)
            plan_data.setdefault("task_id", task_id)
            plan = ExecutionPlan.model_validate(plan_data)
        except (json.JSONDecodeError, PydanticValidationError) as exc:
            logger.error("Invalid plan JSON for task_id=%s: %s", task_id, exc)
            return _fallback_plan(task_id, task_description)

        self.redis.setex(cache_key, CACHE_TTL_SECONDS, plan.model_dump_json())
        return plan


def _require_service() -> PlanningService:
    try:
        return PlanningService()
    except Exception as exc:  # noqa: BLE001
        raise PlanningError(str(exc)) from exc
