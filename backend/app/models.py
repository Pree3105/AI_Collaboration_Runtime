from datetime import datetime, timezone

from sqlalchemy import ForeignKey, Index, JSON, String, Text, Float, Boolean, text, DateTime, CheckConstraint, UniqueConstraint, Integer
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    org_id:Mapped[int]=mapped_column(ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False)
    role: Mapped[str] = mapped_column(String(50), nullable=False, default="user")
    created_at: Mapped[datetime] = mapped_column(default=_utcnow, nullable=False)

    tasks: Mapped[list["Task"]] = relationship(back_populates="created_by_user", cascade="all, delete-orphan")

class Organizations(Base):
    __tablename__ = "organizations"
    id:Mapped[int]=mapped_column(primary_key=True)
    name:Mapped[str]=mapped_column(String(255),nullable=False)
    slug:Mapped[str]=mapped_column(String(255),unique=True)
    created_at:Mapped[datetime]=mapped_column(default=_utcnow, nullable=False) 

class Project(Base):
    __tablename__ = "projects"
    __table_args__ = (
        UniqueConstraint("org_id", "name", name="uq_projects_org_name"),
    )
    id:Mapped[int]=mapped_column(primary_key=True)
    org_id:Mapped[int]=mapped_column(ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False)
    name: Mapped[str] = mapped_column(String(255),unique=True, nullable=False)
    description:Mapped[str | None]=mapped_column(Text)
    tech_stack:Mapped[str | None]=mapped_column(Text)
    guidelines:Mapped[str | None]=mapped_column(Text)
    created_by:Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(default=_utcnow, nullable=False)

class Skill(Base):
    __tablename__ = "skills"
    __table_args__ = (
        Index(
            "uq_skills_org_name_version",
            "org_id", "name", "version",
            unique=True,
            postgresql_where=text("org_id IS NOT NULL"),
        ),
        Index(
            "uq_skills_global_name_version",
            "name", "version",
            unique=True,
            postgresql_where=text("org_id IS NULL"),
        ),
    )
    id:Mapped[int]=mapped_column(primary_key=True)
    org_id:Mapped[int]=mapped_column(ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    version: Mapped[str] = mapped_column(String(50), nullable=False, default="1.0.0")
    description:Mapped[str | None]=mapped_column(Text)
    input_schema:Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    output_schema:Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    system_prompt:Mapped[str] = mapped_column(Text)
    prompt_template:Mapped[str | None] = mapped_column(Text)
    model: Mapped[str | None] = mapped_column(String(100), nullable=True)
    temperature: Mapped[float | None] = mapped_column(Float, nullable=True)
    max_tokens: Mapped[int | None] = mapped_column(nullable=True)
    requires_approval: Mapped[bool] = mapped_column( Boolean, nullable=False, default=False, server_default=text("false"), )
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True, server_default=text("true"), )
    created_by:Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(default=_utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(default=_utcnow, nullable=False)

class WorkflowTemplate(Base):
    __tablename__ = "workflow_templates"

    id: Mapped[int] = mapped_column(primary_key=True)
    org_id: Mapped[int | None] = mapped_column(ForeignKey("organizations.id", ondelete="CASCADE"), nullable=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    steps: Mapped[list] = mapped_column(JSONB, nullable=False, default=list)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow, nullable=False)

class Task(Base):
    __tablename__ = "tasks"
    __table_args__ = (
        Index("ix_tasks_project_status", "project_id", "status"),
        CheckConstraint(
            "status IN ('PENDING', 'RUNNING', 'AWAITING_APPROVAL', "
            "'COMPLETED', 'FAILED', 'CANCELLED')",
            name="ck_tasks_status",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    org_id: Mapped[int] = mapped_column(ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    created_by: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    instruction: Mapped[str] = mapped_column(Text, nullable=False)
    input_data: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    constraints: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    deadline: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    expected_output: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="PENDING", server_default=text("'PENDING'"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow, onupdate=_utcnow, nullable=False)

    created_by_user: Mapped["User"] = relationship(back_populates="tasks")
    workflows: Mapped[list["Workflow"]] = relationship(back_populates="task", cascade="all, delete-orphan")



class Workflow(Base):
    __tablename__ = "workflows"

    id: Mapped[int] = mapped_column(primary_key=True)
    org_id:Mapped[int]=mapped_column(ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False)
    task_id: Mapped[int] = mapped_column(ForeignKey("tasks.id", ondelete="CASCADE"), nullable=False)
    template_id: Mapped[int | None] = mapped_column(ForeignKey("workflow_templates.id", ondelete="SET NULL"), nullable=True)
    # execution_graph_json: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    plan: Mapped[list] = mapped_column(JSONB, nullable=False, default=list)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="PENDING", server_default=text("'PENDING'"))
    current_step_index: Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default=text("0"))
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    neo4j_graph_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    created_by:Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"),nullable=False)
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(default=_utcnow, nullable=False)

    task: Mapped["Task"] = relationship(back_populates="workflows")
    steps: Mapped[list["WorkflowStep"]] = relationship(back_populates="workflow", cascade="all, delete-orphan", order_by="WorkflowStep.step_index")
    artifacts: Mapped[list["Artifact"]] = relationship(back_populates="workflow", cascade="all, delete-orphan")


class Artifact(Base):
    __tablename__ = "artifacts"
    __table_args__ = (
        CheckConstraint(
            "artifact_type IN ('code', 'doc', 'json', 'text')",
            name="ck_artifacts_type",
        ),
        Index("ix_artifacts_org_workflow", "org_id", "workflow_id"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    org_id:Mapped[int]=mapped_column(ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False)
    workflow_id: Mapped[int] = mapped_column(ForeignKey("workflows.id", ondelete="CASCADE"), nullable=False)
    step_id: Mapped[int | None] = mapped_column(ForeignKey("workflow_steps.id", ondelete="SET NULL"), nullable=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    artifact_type: Mapped[str] = mapped_column(String(50), nullable=False)
    mime_type: Mapped[str | None] = mapped_column(String(255), nullable=True) #format of artifact content
    content: Mapped[str] = mapped_column(Text, nullable=True)
    data: Mapped[dict | list | None] = mapped_column(JSONB, nullable=True)
    created_at: Mapped[datetime] = mapped_column(default=_utcnow, nullable=False)

    workflow: Mapped["Workflow"] = relationship(back_populates="artifacts")
    step: Mapped["WorkflowStep | None"] = relationship(back_populates="artifacts")


class WorkflowStep(Base):
    __tablename__ = "workflow_steps"
    __table_args__ = (
        UniqueConstraint("workflow_id", "step_index", name="uq_workflow_steps_workflow_index"),
        Index("ix_workflow_steps_org_status", "org_id", "status"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    org_id: Mapped[int] = mapped_column(ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False)
    workflow_id: Mapped[int] = mapped_column(ForeignKey("workflows.id", ondelete="CASCADE"), nullable=False)
    step_index: Mapped[int] = mapped_column(Integer, nullable=False)
    skill_id: Mapped[int] = mapped_column(ForeignKey("skills.id", ondelete="RESTRICT"), nullable=False)
    depends_on: Mapped[list] = mapped_column(JSONB, nullable=False, default=list)
    input: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    output: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="PENDING", server_default=text("'PENDING'"))
    requires_approval: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, server_default=text("false"))
    approved_by: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    approved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    retry_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default=text("0"))
    error: Mapped[str | None] = mapped_column(Text, nullable=True)
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    workflow: Mapped["Workflow"] = relationship(back_populates="steps")
    artifacts: Mapped[list["Artifact"]] = relationship(back_populates="step")





