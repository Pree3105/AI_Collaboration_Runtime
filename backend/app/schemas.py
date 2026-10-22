from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

EMAIL_PATTERN = r"^[^@\s]+@[^@\s]+\.[^@\s]+$"
TaskStatus = Literal["PENDING", "RUNNING", "AWAITING_APPROVAL", "COMPLETED", "FAILED", "CANCELLED"]


class UserCreate(BaseModel):
    org_id: int
    email: str = Field(pattern=EMAIL_PATTERN)
    password: str = Field(min_length=8)


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    org_id: int
    email: str
    role: str
    created_at: datetime


class CurrentUser(BaseModel):          # plain data object, not an ORM model
    id: int
    org_id: int
    email: str
    role: str


class OrganizationCreate(BaseModel):
    name: str = Field(min_length=1)
    slug: str = Field(min_length=1)


class OrganizationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    slug: str
    created_at: datetime


class ProjectCreate(BaseModel):
    org_id: int
    created_by: int
    name: str = Field(min_length=1)
    description: str | None = None
    tech_stack: str | None = None
    guidelines: str | None = None


class ProjectResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    org_id: int
    name: str
    description: str | None
    tech_stack: str | None
    guidelines: str | None
    created_by: int
    created_at: datetime


class SkillCreate(BaseModel):
    org_id: int
    created_by: int
    name: str = Field(min_length=1)
    version: str = "1.0.0"
    description: str | None = None
    input_schema: dict = Field(default_factory=dict)
    output_schema: dict = Field(default_factory=dict)
    system_prompt: str
    prompt_template: str | None = None
    model: str | None = None
    temperature: float | None = None
    max_tokens: int | None = None
    requires_approval: bool = False
    is_active: bool = True


class SkillResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    org_id: int
    name: str
    version: str
    description: str | None
    input_schema: dict
    output_schema: dict
    system_prompt: str
    prompt_template: str | None
    model: str | None
    temperature: float | None
    max_tokens: int | None
    requires_approval: bool
    is_active: bool
    created_by: int
    created_at: datetime
    updated_at: datetime


class WorkflowTemplateCreate(BaseModel):
    org_id: int | None = None
    name: str = Field(min_length=1)
    description: str | None = None
    steps: list = Field(default_factory=list)


class WorkflowTemplateResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    org_id: int | None
    name: str
    description: str | None
    steps: list
    created_at: datetime


class TaskCreate(BaseModel):
    org_id: int
    project_id: int
    created_by: int
    title: str = Field(min_length=1)
    instruction: str = Field(min_length=1)
    input_data: dict = Field(default_factory=dict)
    constraints: dict = Field(default_factory=dict)
    deadline: datetime | None = None
    expected_output: str = Field(min_length=1)


class TaskUpdate(BaseModel):
    status: TaskStatus


class TaskResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    org_id: int
    project_id: int
    created_by: int
    title: str
    instruction: str
    input_data: dict
    constraints: dict
    deadline: datetime | None
    expected_output: str
    status: str
    created_at: datetime
    updated_at: datetime


class WorkflowResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    org_id: int
    task_id: int
    template_id: int | None
    plan: list
    status: str
    current_step_index: int
    error_message: str | None
    neo4j_graph_id: str | None
    created_by: int
    started_at: datetime | None
    finished_at: datetime | None
    created_at: datetime


class WorkflowStepResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    org_id: int
    workflow_id: int
    step_index: int
    skill_id: int
    depends_on: list
    input: dict
    output: dict | None
    status: str
    requires_approval: bool
    approved_by: int | None
    approved_at: datetime | None
    retry_count: int
    error: str | None
    started_at: datetime | None
    finished_at: datetime | None


class ArtifactResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    org_id: int
    workflow_id: int
    step_id: int | None
    name: str
    artifact_type: str
    mime_type: str | None
    content: str | None
    data: dict | list | None
    created_at: datetime
