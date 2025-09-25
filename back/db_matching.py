from pydantic import BaseModel, EmailStr
from typing import Optional, List, Literal
from datetime import date, datetime


# =========================================================
# USERS
# =========================================================
class UserBase(BaseModel):
    name: str
    email: EmailStr
    role: Literal["admin", "member", "guest"] = "member"


class UserCreate(UserBase):
    password: str


class UserUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None
    role: Optional[Literal["admin", "member", "guest"]] = None


class User(UserBase):
    id: int
    model_config = {"from_attributes": True}


class LoginRequest(BaseModel):
    email: str
    password: str


class LoginResponse(BaseModel):
    id: int
    name: str
    email: str
    role: str
    token: str


# =========================================================
# PROJECTS
# =========================================================
class ProjectBase(BaseModel):
    name: str
    description: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    status: Literal["actif", "archivé"] = "actif"


class ProjectCreate(ProjectBase):
    owner_id: Optional[int] = None


class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    status: Optional[Literal["actif", "archivé"]] = None
    owner_id: Optional[int] = None


class Project(ProjectBase):
    id: int
    owner_id: Optional[int] = None
    created_at: datetime
    model_config = {"from_attributes": True}


class ProjectUserBase(BaseModel):
    project_id: int
    user_id: int
    role: str = "viewer"  # 'owner', 'editor', 'viewer'


class ProjectUserCreate(ProjectUserBase):
    pass


class ProjectUser(ProjectUserBase):
    class Config:
        from_attributes = True


# =========================================================
# TASKS
# =========================================================
class TaskBase(BaseModel):
    title: str
    description: Optional[str] = None
    due_date: Optional[date] = None
    status: Literal["todo", "en cours", "terminé"] = "todo"
    priority: Literal["basse", "moyenne", "haute", "critique"] = "moyenne"


class TaskCreate(TaskBase):
    project_id: int


class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    due_date: Optional[date] = None
    status: Optional[Literal["todo", "en cours", "terminé"]] = None
    priority: Optional[Literal["basse", "moyenne", "haute", "critique"]] = None
    project_id: Optional[int] = None


class Task(TaskBase):
    id: int
    project_id: int
    created_at: datetime
    model_config = {"from_attributes": True}


class TaskWithUsers(Task):
    users: List[User] = []


# =========================================================
# ASSIGNED TASKS
# =========================================================
class AssignedTaskBase(BaseModel):
    task_id: int
    user_id: int


class AssignedTaskCreate(AssignedTaskBase):
    pass


class AssignedTaskDelete(AssignedTaskBase):
    pass


class AssignUsersRequest(BaseModel):
    user_ids: List[int]


class AssignedTask(AssignedTaskBase):
    model_config = {"from_attributes": True}


# =========================================================
# RELATIONS (optionnel)
# =========================================================
class TaskWithProject(Task):
    project: Optional[Project]
    assigned_users: List[User] = []


class ProjectWithTasks(Project):
    tasks: List[Task] = []
