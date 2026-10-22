from sqlalchemy.orm import Session
from app.schemas import ProjectCreate
from app.exceptions import NotFoundError
from app.models import Task, Workflow, Project, User

#valudate request, create db obj, validate response, ret
def create_project(db:Session, project: ProjectCreate, user:User):
    proj=Project(created_by=user.id, name=project.name, description=project.description, techstack=project.tech_stack, org_id=user.org_id)
    try:
        db.add(proj)
        db.commit()
        db.refresh(proj)
    except Exception:
        db.rollback()
        raise

def getProject(db:Session, )->Project:
    project=(
        db.query(Project).join()
    )

