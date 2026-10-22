import pytest
from pydantic import ValidationError

from app.schemas import ExecutionPlan, ExecutionStep, TaskCreate, TaskUpdate, UserCreate


def test_user_create_valid():
    user = UserCreate(email="alice@example.com", password="supersecret")
    assert user.email == "alice@example.com"


def test_user_create_invalid_email():
    with pytest.raises(ValidationError):
        UserCreate(email="not-an-email", password="supersecret")


def test_user_create_invalid_short_password():
    with pytest.raises(ValidationError):
        UserCreate(email="alice@example.com", password="short")


def test_task_create_valid():
    task = TaskCreate(description="Build a report")
    assert task.description == "Build a report"


def test_task_create_invalid_empty_description():
    with pytest.raises(ValidationError):
        TaskCreate(description="")


def test_task_update_valid_status():
    update = TaskUpdate(status="running")
    assert update.status == "running"


def test_task_update_invalid_status():
    with pytest.raises(ValidationError):
        TaskUpdate(status="not-a-real-status")


def test_execution_plan_valid():
    plan = ExecutionPlan(
        task_id=1,
        steps=[
            ExecutionStep(step_id="s1", name="Fetch data", description="Pull source data"),
            ExecutionStep(
                step_id="s2",
                name="Decide",
                description="Choose branch",
                depends_on=["s1"],
                requires_decision=True,
            ),
        ],
    )
    assert len(plan.steps) == 2
    assert plan.steps[1].requires_decision is True


def test_execution_plan_invalid_missing_steps():
    with pytest.raises(ValidationError):
        ExecutionPlan(task_id=1, steps=[])
