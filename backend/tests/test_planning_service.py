import json
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest

from app.schemas import ExecutionPlan
from app.services.workflows.planning import PlanningService

VALID_PLAN_JSON = json.dumps(
    {
        "task_id": 1,
        "steps": [
            {
                "step_id": "step-1",
                "name": "Analyze task",
                "description": "Plan how to accomplish the task",
                "depends_on": [],
                "requires_decision": False,
            }
        ],
        "summary": "Test plan",
    }
)


def _make_openai_response(content: str, prompt_tokens: int = 10, completion_tokens: int = 20):
    return SimpleNamespace(
        choices=[SimpleNamespace(message=SimpleNamespace(content=content))],
        usage=SimpleNamespace(prompt_tokens=prompt_tokens, completion_tokens=completion_tokens),
    )


@pytest.fixture
def service():
    with patch("app.services.workflows.planning.OpenAI") as mock_openai_cls, patch(
        "app.services.workflows.planning.get_redis_client"
    ) as mock_get_redis:
        mock_openai_cls.return_value = MagicMock()
        mock_get_redis.return_value = MagicMock()
        svc = PlanningService()
        yield svc


@pytest.mark.asyncio
async def test_generate_plan_calls_openai_on_cache_miss(service):
    service.redis.get.return_value = None
    service.client.chat.completions.create.return_value = _make_openai_response(VALID_PLAN_JSON)

    plan = await service.generate_plan("Do the thing", task_id=1)

    assert isinstance(plan, ExecutionPlan)
    assert plan.task_id == 1
    assert plan.summary == "Test plan"
    service.client.chat.completions.create.assert_called_once()
    service.redis.setex.assert_called_once()


@pytest.mark.asyncio
async def test_generate_plan_uses_cache_on_hit(service):
    service.redis.get.return_value = VALID_PLAN_JSON

    plan = await service.generate_plan("Do the thing", task_id=1)

    assert isinstance(plan, ExecutionPlan)
    service.client.chat.completions.create.assert_not_called()


@pytest.mark.asyncio
async def test_generate_plan_falls_back_on_invalid_json(service):
    service.redis.get.return_value = None
    service.client.chat.completions.create.return_value = _make_openai_response("not json")

    plan = await service.generate_plan("Do the thing", task_id=1)

    assert plan.summary == "Fallback plan (planning service unavailable)."
    service.redis.setex.assert_not_called()


@pytest.mark.asyncio
async def test_generate_plan_falls_back_on_api_failure(service):
    service.redis.get.return_value = None
    service.client.chat.completions.create.side_effect = Exception("API down")

    plan = await service.generate_plan("Do the thing", task_id=1)

    assert plan.summary == "Fallback plan (planning service unavailable)."


@pytest.mark.asyncio
async def test_generate_plan_logs_token_usage(service, caplog):
    service.redis.get.return_value = None
    service.client.chat.completions.create.return_value = _make_openai_response(
        VALID_PLAN_JSON, prompt_tokens=42, completion_tokens=7
    )

    with caplog.at_level("INFO"):
        await service.generate_plan("Do the thing", task_id=1)

    assert any("prompt_tokens=42" in message for message in caplog.messages)
