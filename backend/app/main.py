"""
MzansiBuilds API Application
"""

from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, HTTPException, Depends
import os
from app.db.database import DatabaseConfig
# User schemas
from app.schemas.user import (
    UserCreate, UserRegisterResponse, UserLogin, UserUpdate, UserResponse
)

# Project schemas
from app.schemas.project import (
    ProjectCreate, ProjectResponse, ProjectUpdate
)

# Update schemas
from app.schemas.update import (
    UpdateCreate, UpdateResponse
)

# Comment schemas
from app.schemas.comment import (
    CommentCreate, CommentResponse
)

# Collaboration schemas
from app.schemas.collaboration import (
    CollaborationCreate, CollaborationResponse, CollaborationUpdate
)

# Celebration schema (wherever you defined it)
from app.schemas.celebration import CelebrationResponse

from app.core.security import hash_password, verify_password, create_access_token
from app.core.dependencies import get_current_user
from typing import Dict

app = FastAPI(title="MzansiBuilds API", version="1.0.0")

db = DatabaseConfig()

@app.on_event("startup")
async def startup_event():
    """Initialize database schema on startup."""
    db.create_database_schema()

# Health check endpoint
@app.get("/api/v1/health")
async def health_check():
    """Check API and database health."""
    db = DatabaseConfig()
    try:
        # Simple query to check database connectivity
        result = db.execute_query("SELECT 1 as health_check")
        if result and result[0].get('health_check') == 1:
            return {"status": "ok", "database": "connected"}
        else:
            return {"status": "error", "database": "query_failed"}
    except Exception as e:
        return {"status": "error", "database": "disconnected", "error": str(e)}

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint."""
    return {"message": "MzansiBuilds API is running"}


# ============================================================================
# Authentication APIs
# ============================================================================

@app.post("/api/auth/register", response_model=UserRegisterResponse)
async def register_user(user_data: UserCreate):
    """Register a new user with hashed password."""
    # Check if email already exists
    existing_user = db.execute_query(
        "SELECT user_id FROM users WHERE email = %s",
        (user_data.email,)
    )

    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    # Hash the password using PBKDF2 with SHA-256
    hashed_password = hash_password(user_data.password)

    # Insert new user
    success = db.execute_update(
        """
        INSERT INTO users (name, email, password_hash, bio)
        VALUES (%s, %s, %s, %s)
        """,
        (user_data.name, user_data.email, hashed_password, user_data.bio)
    )

    if not success:
        raise HTTPException(status_code=500, detail="Failed to create user")

    # Get the new user ID
    user_id = db.get_last_insert_id()
    if user_id is None:
        raise HTTPException(status_code=500, detail="Failed to retrieve user ID")

    return UserRegisterResponse(
        message="User registered successfully",
        user_id=user_id
    )
    

@app.post("/api/auth/login")
async def login_user(user_data: UserLogin):
    """login user"""
    # Fetch user by email
    user = db.execute_query(
        "SELECT user_id, name, email, password_hash FROM users WHERE email = %s",
        (user_data.email,)
    )
    if not user:
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    user = user[0]  # since execute_query returns list of dicts
    
    # Verify password
    if not verify_password(user_data.password, user['password_hash']):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    # Create access token
    access_token = create_access_token(
        data={"user_id": user["user_id"]}
    )
    return {
        "access_token": access_token,
        "token_type": "bearer"
    }

@app.get("/api/users/me", response_model=UserResponse)
async def get_current_user_profile(current_user: dict = Depends(get_current_user)):
    """Get the current authenticated user's profile."""
    return current_user

# ============================================================================
# User APIs
# ============================================================================

@app.get("/api/users/{user_id}", response_model=UserResponse)
async def get_user_profile(user_id: int):
    """Fetch a specific user's profile by user_id."""
    user = db.execute_query(
        "SELECT user_id, name, email, bio, created_at FROM users WHERE user_id = %s AND is_deleted = 0",
        (user_id,)
    )
    if not user or len(user) == 0:
        raise HTTPException(status_code=404, detail="User not found")
    
    return user[0]


@app.put("/api/users/{user_id}", response_model=UserResponse)
async def update_user_profile(user_id: int,user_update: UserUpdate,current_user: dict = Depends(get_current_user)):
    """Update the authenticated user's profile."""
    if current_user["user_id"] != user_id:
        raise HTTPException(status_code=403, detail="Not authorized to update this profile")

    # Build dynamic update query
    update_fields = []
    update_values = []

    if user_update.name is not None:
        update_fields.append("name = %s")
        update_values.append(user_update.name)

    if user_update.bio is not None:
        update_fields.append("bio = %s")
        update_values.append(user_update.bio)

    if not update_fields:
        raise HTTPException(status_code=400, detail="No fields to update")
    
    update_fields.append("updated_at = CURRENT_TIMESTAMP()")  # Automatically update timestamp()

    update_values.append(user_id)  # for WHERE clause

    query = f"UPDATE users SET {', '.join(update_fields)} WHERE user_id = %s AND is_deleted = 0"
    
    success = db.execute_update(query, tuple(update_values))
    
    if not success:
        raise HTTPException(status_code=500, detail="Failed to update user profile")

    # Return updated profile
    updated_user = db.execute_query(
        "SELECT user_id, name, email, bio, created_at FROM users WHERE user_id = %s AND is_deleted = 0",
        (user_id,)
    )
    
    if not updated_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return updated_user[0]


# ============================================================================
# Project APIs
# ============================================================================

@app.post("/api/projects")
async def create_project(project_data: ProjectCreate, current_user: dict = Depends(get_current_user)):
    """Create a new project."""
    query = """
    INSERT INTO projects (user_id, title, description, stage, support_needed)
    VALUES (%s, %s, %s, %s, %s)
    """
    success = db.execute_update(
        query,
        (current_user["user_id"],
         project_data.title,
         project_data.description,
         project_data.stage,
         project_data.support_needed)
    )
    if not success:
        raise HTTPException(status_code=500, detail="Failed to create project")
    
    proj_id = db.get_last_insert_id()
    created_project = db.execute_query(
        "SELECT * FROM projects WHERE proj_id = %s AND is_deleted = 0",
        (proj_id,)
    )
    if not created_project or len(created_project) == 0:
        """ This should never happen if the insert was successful, but we check just in case."""
        raise HTTPException(status_code=404, detail="Project not found after creation")
    
    return created_project[0]

@app.get("/api/projects", response_model=list[ProjectResponse])
async def get_all_projects():
    """Fetch all projects for live feed."""
    projects = db.execute_query(
        """SELECT * FROM projects WHERE is_deleted = 0 ORDER BY created_at DESC"""
    )
    
    if projects is None:
        projects = []
    return projects


@app.get("/api/projects/{proj_id}", response_model=ProjectResponse)
async def get_project(proj_id: int):
    """Fetch a specific project by proj_id."""
    project = db.execute_query(
        "SELECT * FROM projects WHERE proj_id = %s AND is_deleted = 0",
        (proj_id,)
    )
    if not project or len(project) == 0:
        raise HTTPException(status_code=404, detail="Project not found")
    
    return project[0]

@app.get("/api/projects/user/{user_id}", response_model=list[ProjectResponse])
async def get_user_projects(user_id: int):
    """Fetch all projects for a specific user."""
    projects = db.execute_query(
        "SELECT * FROM projects WHERE user_id = %s AND is_deleted = 0 ORDER BY created_at DESC",
        (user_id,)
    )
    if projects is None:
        projects = []
    return projects

@app.put("/api/projects/{proj_id}", response_model=ProjectResponse)
async def update_project(proj_id: int, project_update: ProjectUpdate, current_user: dict = Depends(get_current_user)):
    """Update a project."""
    # Check if project exists and belongs to current user
    existing_project = db.execute_query(
        "SELECT * FROM projects WHERE proj_id = %s AND is_deleted = 0",
        (proj_id,)
    )
    if not existing_project or len(existing_project) == 0:
        raise HTTPException(status_code=404, detail="Project not found")
    
    existing_project = existing_project[0]
    
    if existing_project["user_id"] != current_user["user_id"]:
        raise HTTPException(status_code=403, detail="Not authorized to update this project")

    # Build dynamic update query
    update_fields = []
    update_values = []

    if project_update.title is not None:
        update_fields.append("title = %s")
        update_values.append(project_update.title)

    if project_update.description is not None:
        update_fields.append("description = %s")
        update_values.append(project_update.description)

    if project_update.stage is not None:
        update_fields.append("stage = %s")
        update_values.append(project_update.stage)

    if project_update.support_needed is not None:
        update_fields.append("support_needed = %s")
        update_values.append(project_update.support_needed)

    if not update_fields:
        raise HTTPException(status_code=400, detail="No fields to update")
    
    update_fields.append("updated_at = CURRENT_TIMESTAMP()")  # Automatically update timestamp()

    update_values.append(proj_id)  # for WHERE clause

    query = f"UPDATE projects SET {', '.join(update_fields)} WHERE proj_id = %s AND is_deleted = 0"
    
    success = db.execute_update(query, tuple(update_values))
    
    if not success:
        raise HTTPException(status_code=500, detail="Failed to update project")

    # Return updated project
    updated_project = db.execute_query(
        "SELECT * FROM projects WHERE proj_id = %s AND is_deleted = 0",
        (proj_id,)
    )
    
    if not updated_project or len(updated_project) == 0:
        """ This should never happen if the update was successful, but we check just in case. """
        raise HTTPException(status_code=404, detail="Project not found after update")
    
    return updated_project[0]

@app.delete("/api/projects/{proj_id}")
async def delete_project(proj_id: int, current_user: dict = Depends(get_current_user)):
    """Soft delete a project."""
    # Check if project exists and belongs to current user
    existing_project = db.execute_query(
        "SELECT * FROM projects WHERE proj_id = %s AND is_deleted = 0",
        (proj_id,)
    )
    if not existing_project or len(existing_project) == 0:
        raise HTTPException(status_code=404, detail="Project not found")
    
    existing_project = existing_project[0]
    
    if existing_project["user_id"] != current_user["user_id"]:
        raise HTTPException(status_code=403, detail="Not authorized to delete this project")

    # Soft delete the project
    success = db.execute_update(
        "UPDATE projects SET is_deleted = 1, updated_at = CURRENT_TIMESTAMP() WHERE proj_id = %s",
        (proj_id,)
    )
    
    if not success:
        raise HTTPException(status_code=500, detail="Failed to delete project")

    return {"message": "Project deleted successfully"}

# ============================================================================
# Update APIs
# ============================================================================

@app.post("/api/updates", response_model=UpdateResponse)
async def create_update(update: UpdateCreate, current_user: dict = Depends(get_current_user)):
    """Create a new update."""
    # Check if the project exists and belongs to the current user
    project = db.execute_query(
        "SELECT * FROM projects WHERE proj_id = %s AND is_deleted = 0",
        (update.project_id,)
    )
    if not project or len(project) == 0:
        raise HTTPException(status_code=404, detail="Project not found")

    project = project[0]
    
    is_owner = project["user_id"] == current_user["user_id"]
    collaborator = db.execute_query(
        """SELECT * FROM collaboration_request
        WHERE proj_id = %s AND user_id = %s AND status = 'accepted' AND is_deleted = 0 """,
        (update.project_id, current_user["user_id"])
    )
    is_collaborator = bool(collaborator)
    
    if not( is_owner or is_collaborator):
        raise HTTPException(status_code=403, detail="Not authorized to create updates for this project")

    # Insert the new update
    success = db.execute_update(
        "INSERT INTO updates (project_id, user_id, content) VALUES (%s, %s, %s)",
        (update.project_id, current_user["user_id"], update.content)
    )

    if not success:
        raise HTTPException(status_code=500, detail="Failed to create update")

    # Return the created update
    created_update = db.execute_query(
        "SELECT * FROM updates WHERE project_id = %s AND user_id = %s AND content = %s",
        (update.project_id, current_user["user_id"], update.content)
    )

    if not created_update or len(created_update) == 0:
        """ This should never happen if the insert was successful, but we check just in case. """
        raise HTTPException(status_code=404, detail="Update not found after creation")

    return created_update[0]


@app.get("/api/updates", response_model=list[UpdateResponse])
async def get_all_updates():
    """Fetch all updates for live feed."""
    updates = db.execute_query(
        """SELECT * FROM updates WHERE is_deleted = 0 ORDER BY created_at DESC"""
    )
    
    if updates is None:
        updates = []
    return updates

@app.get("/api/projects/{proj_id}/updates", response_model=list[UpdateResponse])
async def get_project_updates(proj_id: int):
    """Fetch all updates for a specific project."""
    updates = db.execute_query(
        """SELECT * FROM updates WHERE project_id = %s AND is_deleted = 0 ORDER BY created_at DESC""",
        (proj_id,)
    )
    
    if updates is None:
        updates = []
    return updates

@app.delete("/api/updates/{update_id}")
async def delete_update(update_id: int, current_user: dict = Depends(get_current_user)):
    """Soft delete an update."""
    # Check if update exists and belongs to current user
    existing_update = db.execute_query(
        "SELECT * FROM updates WHERE update_id = %s AND is_deleted = 0",
        (update_id,)
    )
    if not existing_update or len(existing_update) == 0:
        raise HTTPException(status_code=404, detail="Update not found")

    existing_update = existing_update[0]

    if existing_update["user_id"] != current_user["user_id"]:
        raise HTTPException(status_code=403, detail="Not authorized to delete this update")

    # Soft delete the update
    success = db.execute_update(
        "UPDATE updates SET is_deleted = 1, updated_at = CURRENT_TIMESTAMP() WHERE update_id = %s",
        (update_id,)
    )

    if not success:
        raise HTTPException(status_code=500, detail="Failed to delete update")

    return {"message": "Update deleted successfully"}

# ============================================================================
# Comments APIs
# ============================================================================

@app.post("/api/comments", response_model=CommentResponse)
async def create_comment(comment: CommentCreate,current_user: dict = Depends(get_current_user)):
    # Check update exists
    update = db.execute_query(
        "SELECT * FROM updates WHERE update_id = %s AND is_deleted = 0",
        (comment.update_id,)
    )

    if not update:
        raise HTTPException(status_code=404, detail="Update not found")

    # Insert comment
    success = db.execute_update(
        """
        INSERT INTO comment (update_id, user_id, content)
        VALUES (%s, %s, %s)
        """,
        (comment.update_id, current_user["user_id"], comment.content)
    )

    if not success:
        raise HTTPException(status_code=500, detail="Failed to create comment")

    com_id = db.get_last_insert_id()

    created_comment = db.execute_query(
        "SELECT * FROM comment WHERE com_id = %s AND is_deleted = 0",
        (com_id,)
    )

    return created_comment[0]

@app.get("/api/updates/{update_id}/comments", response_model=list[CommentResponse])
async def get_update_comments(update_id: int):
    """Fetch all comments for a specific update."""
    comments = db.execute_query(
        """SELECT * FROM comment WHERE update_id = %s AND is_deleted = 0 ORDER BY created_at ASC""",
        (update_id,)
    )
    
    if comments is None:
        comments = []
    return comments

@app.delete("/api/comments/{com_id}")
async def delete_comment(com_id: int, current_user: dict = Depends(get_current_user)):
    """Soft delete a comment."""
    # Check if comment exists and belongs to current user
    existing_comment = db.execute_query(
        "SELECT * FROM comment WHERE com_id = %s AND is_deleted = 0",
        (com_id,)
    )
    if not existing_comment or len(existing_comment) == 0:
        raise HTTPException(status_code=404, detail="Comment not found")

    existing_comment = existing_comment[0]

    if existing_comment["user_id"] != current_user["user_id"]:
        raise HTTPException(status_code=403, detail="Not authorized to delete this comment")

    # Soft delete the comment
    success = db.execute_update(
        "UPDATE comment SET is_deleted = 1, updated_at = CURRENT_TIMESTAMP() WHERE com_id = %s",
        (com_id,)
    )

    if not success:
        raise HTTPException(status_code=500, detail="Failed to delete comment")

    return {"message": "Comment deleted successfully"}


# ============================================================================
# Collaboration Request APIs
# ============================================================================

@app.post("/api/collaborations", response_model=CollaborationResponse)
async def create_collaboration_request(collab: CollaborationCreate,current_user: dict = Depends(get_current_user)):
    # 1. Check project exists
    project = db.execute_query(
        "SELECT * FROM project WHERE proj_id = %s AND is_deleted = 0",
        (collab.project_id,)
    )

    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    # 2. Prevent owner from requesting own project
    if project[0]["user_id"] == current_user["user_id"]:
        raise HTTPException(status_code=400, detail="Cannot collaborate on your own project")

    # 3. Prevent duplicate requests
    existing = db.execute_query(
        """
        SELECT * FROM collaboration_request
        WHERE project_id = %s AND user_id = %s AND is_deleted = 0
        """,
        (collab.project_id, current_user["user_id"])
    )

    if existing:
        raise HTTPException(status_code=400, detail="Request already exists")

    # 4. Insert request
    success = db.execute_update(
        """
        INSERT INTO collaboration_request (project_id, user_id, message)
        VALUES (%s, %s, %s)
        """,
        (collab.project_id, current_user["user_id"], collab.message)
    )

    if not success:
        raise HTTPException(status_code=500, detail="Failed to create request")

    collab_id = db.get_last_insert_id()

    created = db.execute_query(
        "SELECT * FROM collaboration_request WHERE collab_id = %s",
        (collab_id,)
    )

    return created[0]

@app.get("/api/projects/{project_id}/collaborations", response_model=list[CollaborationResponse])
async def get_project_collaborations(project_id: int,current_user: dict = Depends(get_current_user)):
    project = db.execute_query(
        "SELECT * FROM project WHERE proj_id = %s AND is_deleted = 0",
        (project_id,)
    )

    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    # Only owner can view requests
    if project[0]["user_id"] != current_user["user_id"]:
        raise HTTPException(status_code=403, detail="Not authorized")

    requests = db.execute_query(
        """
        SELECT * FROM collaboration_request
        WHERE project_id = %s AND is_deleted = 0
        ORDER BY created_at DESC
        """,
        (project_id,)
    )

    return requests or []

@app.patch("/api/collaborations/{collab_id}", response_model=CollaborationResponse)
async def update_collaboration_status(collab_id: int,update: CollaborationUpdate,current_user: dict = Depends(get_current_user)):
    # 1. Get request
    collab = db.execute_query(
        "SELECT * FROM collaboration_request WHERE collab_id = %s AND is_deleted = 0",
        (collab_id,)
    )

    if not collab:
        raise HTTPException(status_code=404, detail="Request not found")

    project_id = collab[0]["project_id"]

    # 2. Check project ownership
    project = db.execute_query(
        "SELECT * FROM project WHERE proj_id = %s",
        (project_id,)
    )

    if project[0]["user_id"] != current_user["user_id"]:
        raise HTTPException(status_code=403, detail="Not authorized")

    # 3. Update status
    success = db.execute_update(
        """
        UPDATE collaboration_request
        SET status = %s, updated_at = CURRENT_TIMESTAMP
        WHERE collab_id = %s
        """,
        (update.status, collab_id)
    )

    if not success:
        raise HTTPException(status_code=500, detail="Failed to update request")

    updated = db.execute_query(
        "SELECT * FROM collaboration_request WHERE collab_id = %s",
        (collab_id,)
    )

    return updated[0]

@app.get("/api/collaborations/me", response_model=list[CollaborationResponse])
async def get_my_collaborations(current_user: dict = Depends(get_current_user)):
    """Fetch all collaboration requests for the current user."""
    requests = db.execute_query(
        """
        SELECT cr.*, p.title
        FROM collaboration_request cr
        JOIN project p ON cr.project_id = p.proj_id
        WHERE cr.user_id = %s AND cr.is_deleted = 0
        ORDER BY cr.created_at DESC
        """,
        (current_user["user_id"],)
    )
    if requests is None:
        requests = []
    return requests


# ============================================================================
# Celebration Wall API
# ============================================================================

@app.get("/api/celebrations", response_model=list[CelebrationResponse])
async def get_celebration_wall():
    """Fetch recently completed projects for the celebration wall."""
    
    celebrations = db.execute_query(
        """
        SELECT 
            p.proj_id,
            p.title,
            p.description,
            p.updated_at,
            u.user_id,
            u.name,
            COUNT(up.update_id) AS total_updates
        FROM project p
        JOIN users u ON p.user_id = u.user_id
        LEFT JOIN updates up 
            ON up.project_id = p.proj_id 
            AND up.is_deleted = 0
        WHERE 
            p.stage = 'Completed'
            AND p.is_deleted = 0
        GROUP BY 
            p.proj_id, p.title, p.description, p.updated_at,
            u.user_id, u.name
        ORDER BY p.updated_at DESC
        """
    )
    if celebrations is None:
        celebrations = []
    return celebrations