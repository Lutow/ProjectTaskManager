import sys
from pathlib import Path
from datetime import datetime, timezone
from fastapi import FastAPI, HTTPException, Query, Body, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer
import mysql.connector
from mysql.connector import Error

sys.path.append(str(Path(__file__).parent))
from db_matching import *
from Auth import verify_password, get_password_hash, create_access_token, decode_token, JWTError

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

'''
def get_db_connection():
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password=X,
            database="Task_Manager"
        )
        return connection
    except Error as e:
        print(f"Erreur de connexion à MySQL : {e}")
        return None
'''


def get_db_connection():
    try:
        connection = mysql.connector.connect(
            host="db",
            user="taskuser",
            password="taskpassword",
            database="Task_Manager"
        )
        return connection
    except Error as e:
        print(f"Erreur de connexion à MySQL : {e}")
        return None


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


def get_current_user(token: str = Depends(oauth2_scheme)):
    """
    Vérifie le JWT et retourne l'utilisateur courant
    """
    try:
        payload = decode_token(token)
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Token invalide")
        return {"id": int(user_id)}
    except JWTError:
        raise HTTPException(status_code=401, detail="Token invalide ou expiré")


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}


@app.get("/users", response_model=List[User])
async def get_users():
    connection = get_db_connection()
    if not connection:
        raise HTTPException(status_code=500, detail="Erreur de connexion à la base de données")

    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM Users")
        users = cursor.fetchall()
    except Error as e:
        raise HTTPException(status_code=500, detail=f"Erreur SQL : {e}")
    finally:
        cursor.close()
        connection.close()

    return users


@app.post("/users", response_model=User, status_code=201)
async def create_user(user: UserCreate):
    connection = get_db_connection()
    if not connection:
        raise HTTPException(status_code=500, detail="Erreur de connexion à la base de données")

    try:
        cursor = connection.cursor()
        query = """
        INSERT INTO Users (name, email, password, role)
        VALUES (%s, %s, %s, %s)
        """
        values = (
            user.name,
            user.email,
            get_password_hash(user.password),
            user.role
        )
        cursor.execute(query, values)
        connection.commit()
        user_id = cursor.lastrowid
    except Error as e:
        raise HTTPException(status_code=500, detail=f"Erreur SQL : {e}")
    finally:
        cursor.close()
        connection.close()

    return {**user.model_dump(), "id": user_id}


@app.post("/login", response_model=LoginResponse)
async def login_user(credentials: LoginRequest):
    connection = get_db_connection()
    if not connection:
        raise HTTPException(status_code=500, detail="Erreur de connexion à la base de données")

    try:
        cursor = connection.cursor(dictionary=True)
        query = "SELECT * FROM Users WHERE email = %s"
        cursor.execute(query, (credentials.email,))
        user = cursor.fetchone()

        if not user:
            raise HTTPException(status_code=401, detail="Utilisateur non trouvé")

        if not verify_password(credentials.password, user["password"]):
            raise HTTPException(status_code=401, detail="Mot de passe incorrect")

        # JWT
        token = create_access_token({"sub": str(user["id"])})

        return {
            "id": user["id"],
            "name": user["name"],
            "email": user["email"],
            "role": user["role"],
            "token": token,
        }

    except Error as e:
        raise HTTPException(status_code=500, detail=f"Erreur SQL : {e}")
    finally:
        cursor.close()
        connection.close()


@app.get("/projects", response_model=List[Project])
async def get_projects():
    connection = get_db_connection()
    if not connection:
        raise HTTPException(status_code=500, detail="Erreur de connexion à la base de données")

    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM Projects")
        projects = cursor.fetchall()
    except Error as e:
        raise HTTPException(status_code=500, detail=f"Erreur SQL : {e}")
    finally:
        cursor.close()
        connection.close()

    return projects


@app.get("/projects/{id}", response_model=List[Project])
async def get_projects_by_id(id: int):
    connection = get_db_connection()
    if not connection:
        raise HTTPException(status_code=500, detail="Erreur de connexion à la base de données")

    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM Projects WHERE id = %s", (id,))
        projects = cursor.fetchall()
    except Error as e:
        raise HTTPException(status_code=500, detail=f"Erreur SQL : {e}")
    finally:
        cursor.close()
        connection.close()

    return projects


@app.post("/projects", response_model=Project, status_code=201)
async def create_project(project: ProjectCreate, current_user: dict = Depends(get_current_user)):
    user_id = current_user["id"]
    connection = get_db_connection()
    if not connection:
        raise HTTPException(status_code=500, detail="Erreur de connexion à la base de données")
    try:
        cursor = connection.cursor()
        query = """
        INSERT INTO Projects (name, description, start_date, end_date, status, owner_id)
        VALUES (%s, %s, %s, %s, %s, %s)
        """
        values = (
            project.name,
            project.description,
            project.start_date,
            project.end_date,
            project.status,
            user_id
        )
        cursor.execute(query, values)
        connection.commit()
        project_id = cursor.lastrowid
    except Error as e:
        raise HTTPException(status_code=500, detail=f"Erreur SQL : {e}")
    finally:
        cursor.close()
        connection.close()
    return {**project.model_dump(), "id": project_id, "created_at": datetime.now(timezone.utc).isoformat()}


@app.put("/projects/{id}", response_model=Project)
async def update_project(id: int, project: ProjectUpdate = Body(...)):
    connection = get_db_connection()
    if not connection:
        raise HTTPException(status_code=500, detail="Erreur de connexion à la base de données")
    try:
        cursor = connection.cursor(dictionary=True)

        cursor.execute("SELECT * FROM Projects WHERE id = %s", (id,))
        existing_project = cursor.fetchone()
        if not existing_project:
            raise HTTPException(status_code=404, detail="Projet non trouvé")

        update_fields = []
        values = []

        if project.name is not None:
            update_fields.append("name = %s")
            values.append(project.name)
        if project.description is not None:
            update_fields.append("description = %s")
            values.append(project.description)
        if project.start_date is not None:
            update_fields.append("start_date = %s")
            values.append(project.start_date)
        if project.end_date is not None:
            update_fields.append("end_date = %s")
            values.append(project.end_date)
        if project.status is not None:
            update_fields.append("status = %s")
            values.append(project.status)

        if not update_fields:
            raise HTTPException(status_code=400, detail="Aucun champ à mettre à jour")

        query = f"UPDATE Projects SET {', '.join(update_fields)} WHERE id = %s"
        values.append(id)

        cursor.execute(query, tuple(values))
        connection.commit()

        cursor.execute("SELECT * FROM Projects WHERE id = %s", (id,))
        updated_project = cursor.fetchone()

    except Error as e:
        raise HTTPException(status_code=500, detail=f"Erreur SQL : {e}")
    finally:
        cursor.close()
        connection.close()

    return updated_project


@app.delete("/projects/{id}", status_code=204)
async def delete_project(id: int):
    connection = get_db_connection()
    if not connection:
        raise HTTPException(status_code=500, detail="Erreur connexion DB")

    try:
        cursor = connection.cursor()
        cursor.execute("DELETE FROM Projects WHERE id = %s", (id,))
        connection.commit()
    except Error as e:
        raise HTTPException(status_code=500, detail=f"Erreur SQL : {e}")
    finally:
        cursor.close()
        connection.close()

    return {"message": f"Projet : {id} supprimé"}


@app.post("/project-users", response_model=ProjectUser, status_code=201)
async def add_user_to_project(project_user: ProjectUserCreate):
    connection = get_db_connection()
    if not connection:
        raise HTTPException(status_code=500, detail="Erreur connexion DB")

    try:
        cursor = connection.cursor()
        query = """
        INSERT INTO ProjectUsers (project_id, user_id, role)
        VALUES (%s, %s, %s)
        """
        values = (project_user.project_id, project_user.user_id, project_user.role)
        cursor.execute(query, values)
        connection.commit()
    except Error as e:
        raise HTTPException(status_code=500, detail=f"Erreur SQL : {e}")
    finally:
        cursor.close()
        connection.close()

    return project_user


@app.get("/project-users/{project_id}", response_model=List[ProjectUser])
async def get_project_users(project_id: int):
    connection = get_db_connection()
    if not connection:
        raise HTTPException(status_code=500, detail="Erreur connexion DB")

    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM ProjectUsers WHERE project_id = %s", (project_id,))
        users = cursor.fetchall()
    except Error as e:
        raise HTTPException(status_code=500, detail=f"Erreur SQL : {e}")
    finally:
        cursor.close()
        connection.close()

    return users


@app.delete("/project-users/{project_id}/{user_id}", status_code=204)
async def remove_user_from_project(project_id: int, user_id: int):
    connection = get_db_connection()
    if not connection:
        raise HTTPException(status_code=500, detail="Erreur connexion DB")

    try:
        cursor = connection.cursor()
        cursor.execute(
            "DELETE FROM ProjectUsers WHERE project_id = %s AND user_id = %s",
            (project_id, user_id),
        )
        connection.commit()
    except Error as e:
        raise HTTPException(status_code=500, detail=f"Erreur SQL : {e}")
    finally:
        cursor.close()
        connection.close()

    return {"message": "Utilisateur retiré du projet"}


@app.get("/my-projects", response_model=List[Project])
async def get_my_projects(current_user: dict = Depends(get_current_user)):
    connection = get_db_connection()
    if not connection:
        raise HTTPException(status_code=500, detail="Erreur connexion DB")

    try:
        cursor = connection.cursor(dictionary=True)
        query = """
        SELECT DISTINCT p.*
        FROM Projects p
        LEFT JOIN ProjectUsers pu ON p.id = pu.project_id
        WHERE p.owner_id = %s OR pu.user_id = %s
        """
        cursor.execute(query, (current_user["id"], current_user["id"]))
        projects = cursor.fetchall()
    except Error as e:
        raise HTTPException(status_code=500, detail=f"Erreur SQL : {e}")
    finally:
        cursor.close()
        connection.close()

    return projects


@app.get("/tasks", response_model=List[Task])
async def get_tasks():
    connection = get_db_connection()
    if not connection:
        raise HTTPException(status_code=500, detail="Erreur de connexion à la base de données")

    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM Tasks")
        tasks = cursor.fetchall()
    except Error as e:
        raise HTTPException(status_code=500, detail=f"Erreur SQL : {e}")
    finally:
        cursor.close()
        connection.close()

    return tasks


@app.get("/projects/{project_id}/tasks", response_model=List[TaskWithUsers])
async def get_tasks_by_project(project_id: int):
    connection = get_db_connection()
    if not connection:
        raise HTTPException(status_code=500, detail="Erreur connexion DB")

    try:
        cursor = connection.cursor(dictionary=True)

        # Get tasks
        cursor.execute("SELECT * FROM Tasks WHERE project_id = %s", (project_id,))
        tasks = cursor.fetchall()

        enriched_tasks = []
        for task in tasks:
            # Get assigned users
            cursor.execute("""
                SELECT u.id, u.name, u.email
                FROM Users u
                JOIN AssignedTasks a ON u.id = a.user_id
                WHERE a.task_id = %s
            """, (task["id"],))
            users = cursor.fetchall()

            task["users"] = users  # attach list of user dicts
            enriched_tasks.append(task)

    except Error as e:
        raise HTTPException(status_code=500, detail=f"Erreur SQL : {e}")
    finally:
        cursor.close()
        connection.close()

    return enriched_tasks


@app.post("/tasks", response_model=Task, status_code=201)
async def create_task(task: TaskCreate):
    connection = get_db_connection()
    if not connection:
        raise HTTPException(status_code=500, detail="Erreur de connexion à la base de données")

    try:
        cursor = connection.cursor()
        query = """
        INSERT INTO Tasks (title, description, due_date, status, priority, project_id)
        VALUES (%s, %s, %s, %s, %s, %s)
        """
        values = (
            task.title,
            task.description,
            task.due_date,
            task.status,
            task.priority,
            task.project_id
        )
        cursor.execute(query, values)
        connection.commit()
        task_id = cursor.lastrowid

    except Error as e:
        raise HTTPException(status_code=500, detail=f"Erreur SQL : {e}")
    finally:
        cursor.close()
        connection.close()

    return {**task.model_dump(), "id": task_id, "created_at": datetime.now(timezone.utc).isoformat()}


@app.put("/tasks/{id}", response_model=Task)
async def update_task(id: int, task: TaskUpdate = Body(...)):
    connection = get_db_connection()
    if not connection:
        raise HTTPException(status_code=500, detail="Erreur de connexion à la base de données")
    try:
        cursor = connection.cursor(dictionary=True)

        cursor.execute("SELECT * FROM Tasks WHERE id = %s", (id,))
        existing_task = cursor.fetchone()
        if not existing_task:
            raise HTTPException(status_code=404, detail="Tâche non trouvée")

        update_fields = []
        values = []

        if task.title is not None:
            update_fields.append("title = %s")
            values.append(task.title)
        if task.description is not None:
            update_fields.append("description = %s")
            values.append(task.description)
        if task.due_date is not None:
            update_fields.append("due_date = %s")
            values.append(task.due_date)
        if task.status is not None:
            update_fields.append("status = %s")
            values.append(task.status)
        if task.status is not None:
            update_fields.append("status = %s")
            values.append(task.status)
        if task.priority is not None:
            update_fields.append("priority = %s")
            values.append(task.priority)

        if not update_fields:
            raise HTTPException(status_code=400, detail="Aucun champ à mettre à jour")

        query = f"UPDATE Tasks SET {', '.join(update_fields)} WHERE id = %s"
        values.append(id)

        cursor.execute(query, tuple(values))
        connection.commit()

        cursor.execute("SELECT * FROM Tasks WHERE id = %s", (id,))
        updated_task = cursor.fetchone()

    except Error as e:
        raise HTTPException(status_code=500, detail=f"Erreur SQL : {e}")
    finally:
        cursor.close()
        connection.close()

    return updated_task


@app.delete("/tasks/{id}")
async def delete_task_by_id(id: int):
    connection = get_db_connection()
    if not connection:
        raise HTTPException(status_code=500, detail="Erreur connexion DB")

    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute("DELETE FROM Tasks WHERE id = %s", (id,))
        connection.commit()
    except Error as e:
        raise HTTPException(status_code=500, detail=f"Erreur SQL : {e}")
    finally:
        cursor.close()
        connection.close()

    return {"message": f"Tâche : {id} supprimée"}


@app.get("/tasks/assigned", response_model=List[AssignedTask])
async def get_assigned_tasks():
    connection = get_db_connection()
    if not connection:
        raise HTTPException(status_code=500, detail="Erreur connexion DB")

    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM AssignedTasks")
        assigned = cursor.fetchall()
    except Error as e:
        raise HTTPException(status_code=500, detail=f"Erreur SQL : {e}")
    finally:
        cursor.close()
        connection.close()

    return assigned


@app.get("/tasks/{task_id}/users")
async def get_task_users(task_id: int):
    connection = get_db_connection()
    if not connection:
        raise HTTPException(status_code=500, detail="Erreur DB")
    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute("""
            SELECT u.id, u.name, u.email
            FROM Users u
            JOIN AssignedTasks a ON u.id = a.user_id
            WHERE a.task_id = %s
        """, (task_id,))
        users = cursor.fetchall()
    finally:
        cursor.close()
        connection.close()
    return users


@app.post("/tasks/{task_id}/assign-users")
async def assign_users_to_task(task_id: int, payload: AssignUsersRequest):
    connection = get_db_connection()
    if not connection:
        raise HTTPException(status_code=500, detail="Erreur DB")
    try:
        cursor = connection.cursor()
        cursor.execute("DELETE FROM AssignedTasks WHERE task_id = %s", (task_id,))
        for user_id in payload.user_ids:
            cursor.execute(
                "INSERT INTO AssignedTasks (task_id, user_id) VALUES (%s, %s)",
                (task_id, user_id),
            )
        connection.commit()
    except Error as e:
        raise HTTPException(status_code=500, detail=f"Erreur SQL : {e}")
    finally:
        cursor.close()
        connection.close()
    return {"task_id": task_id, "assigned_users": payload.user_ids}
