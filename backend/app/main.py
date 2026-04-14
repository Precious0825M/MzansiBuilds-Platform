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
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="MzansiBuilds API", version="1.0.0")

app.add_middleware(
     CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
    user_id = db.execute_insert(
        """
        INSERT INTO users (name, email, password_hash, bio)
        VALUES (%s, %s, %s, %s)
        """,
        (user_data.name, user_data.email, hashed_password, user_data.bio)
    )

    if user_id is None:
        raise HTTPException(status_code=500, detail="Failed to create user")

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

@app.get("/api/auth/me", response_model=UserResponse)
async def get_auth_me(current_user: dict = Depends(get_current_user)):
    """Get the current authenticated user's profile (alias for /api/users/me)."""
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
    proj_id = db.execute_insert(
        query,
        (current_user["user_id"],
         project_data.title,
         project_data.description,
         project_data.stage,
         project_data.support_needed)
    )
    
    if proj_id is None:
        raise HTTPException(status_code=500, detail="Failed to create project")
    
    created_project = db.execute_query(
        "SELECT * FROM projects WHERE proj_id = %s AND is_deleted = 0",
        (proj_id,)
    )
    if not created_project or len(created_project) == 0:
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
    update_id = db.execute_insert(
        "INSERT INTO updates (project_id, user_id, content) VALUES (%s, %s, %s)",
        (update.project_id, current_user["user_id"], update.content)
    )

    if update_id is None:
        raise HTTPException(status_code=500, detail="Failed to create update")

    # Return the created update
    created_update = db.execute_query(
        "SELECT * FROM updates WHERE update_id = %s",
        (update_id,)
    )

    if not created_update or len(created_update) == 0:
        raise HTTPException(status_code=404, detail="Update not found after creation")

    return created_update[0]


@app.get("/api/updates")
async def get_all_updates(current_user: dict = Depends(get_current_user)):
    """Fetch all updates for live feed with enriched data (project info, comments, collaboration status)."""
    updates = db.execute_query(
        """SELECT * FROM updates WHERE is_deleted = 0 ORDER BY created_at DESC"""
    )
    
    if updates is None:
        updates = []
    
    # Enrich each update with project info, author info, comments, and collaboration status
    enriched_updates = []
    for update in updates:
        # Get project info
        project_data = db.execute_query(
            "SELECT proj_id, title, user_id FROM projects WHERE proj_id = %s AND is_deleted = 0",
            (update['project_id'],)
        )
        project = project_data[0] if project_data else None
        
        # Get author info
        author = None
        if update.get('user_id'):
            author_data = db.execute_query(
                "SELECT user_id, name, email, bio FROM users WHERE user_id = %s AND is_deleted = 0",
                (update['user_id'],)
            )
            if author_data:
                author = author_data[0]
        
        # Get project owner info
        project_owner = None
        if project and project.get('user_id'):
            owner_data = db.execute_query(
                "SELECT user_id, name FROM users WHERE user_id = %s AND is_deleted = 0",
                (project['user_id'],)
            )
            if owner_data:
                project_owner = owner_data[0]
        
        # Get comments
        comments_data = db.execute_query(
            """SELECT c.com_id, c.content, c.user_id, u.name, c.created_at 
               FROM comment c 
               JOIN users u ON c.user_id = u.user_id 
               WHERE c.update_id = %s AND c.is_deleted = 0 
               ORDER BY c.created_at ASC""",
            (update['update_id'],)
        )
        comments = comments_data or []
        
        # Check collaboration request status for current user
        collab_status = None
        if project:
            collab_req = db.execute_query(
                """SELECT status FROM collaboration_request 
                   WHERE project_id = %s AND user_id = %s AND is_deleted = 0""",
                (project['proj_id'], current_user['user_id'])
            )
            if collab_req:
                collab_status = collab_req[0]['status']
        
        enriched_updates.append({
            'update_id': update['update_id'],
            'project_id': update['project_id'],
            'user_id': update['user_id'],
            'content': update['content'],
            'created_at': update['created_at'],
            'author': author,
            'project': project,
            'project_owner': project_owner,
            'comments': comments,
            'collab_status': collab_status,
            'is_owner': project and project['user_id'] == current_user['user_id']
        })
    
    return enriched_updates

@app.get("/api/projects/{proj_id}/updates", response_model=list[dict])
async def get_project_updates(proj_id: int):
    """Fetch all updates for a specific project with nested comments and author info."""
    updates = db.execute_query(
        """SELECT * FROM updates WHERE project_id = %s AND is_deleted = 0 ORDER BY created_at DESC""",
        (proj_id,)
    )
    
    if updates is None:
        updates = []
    
    # Enrich each update with author info and comments
    enriched_updates = []
    for update in updates:
        # Get author info
        author = None
        if update.get('user_id'):
            author_data = db.execute_query(
                "SELECT user_id, name, email, bio FROM users WHERE user_id = %s AND is_deleted = 0",
                (update['user_id'],)
            )
            if author_data and len(author_data) > 0:
                author = author_data[0]
        
        # Get comments for this update
        comments_data = db.execute_query(
            """SELECT * FROM comment WHERE update_id = %s AND is_deleted = 0 ORDER BY created_at ASC""",
            (update['update_id'],)
        )
        
        # Enrich comments with author info
        comments = []
        if comments_data:
            for comment in comments_data:
                comment_author = None
                if comment.get('user_id'):
                    comment_author_data = db.execute_query(
                        "SELECT user_id, name FROM users WHERE user_id = %s AND is_deleted = 0",
                        (comment['user_id'],)
                    )
                    if comment_author_data and len(comment_author_data) > 0:
                        comment_author = comment_author_data[0]
                
                comments.append({
                    'com_id': comment['com_id'],
                    'update_id': comment['update_id'],
                    'user_id': comment['user_id'],
                    'content': comment['content'],
                    'created_at': comment['created_at'],
                    'author': comment_author
                })
        
        enriched_updates.append({
            'update_id': update['update_id'],
            'project_id': update['project_id'],
            'user_id': update['user_id'],
            'content': update['content'],
            'created_at': update['created_at'],
            'author': author,
            'comments': comments
        })
    
    return enriched_updates

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
    com_id = db.execute_insert(
        """
        INSERT INTO comment (update_id, user_id, content)
        VALUES (%s, %s, %s)
        """,
        (comment.update_id, current_user["user_id"], comment.content)
    )

    if com_id is None:
        raise HTTPException(status_code=500, detail="Failed to create comment")

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
        "SELECT * FROM projects WHERE proj_id = %s AND is_deleted = 0",
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
    collab_id = db.execute_insert(
        """
        INSERT INTO collaboration_request (project_id, user_id, message)
        VALUES (%s, %s, %s)
        """,
        (collab.project_id, current_user["user_id"], collab.message)
    )

    if collab_id is None:
        raise HTTPException(status_code=500, detail="Failed to create request")

    created = db.execute_query(
        "SELECT * FROM collaboration_request WHERE collab_id = %s",
        (collab_id,)
    )

    return created[0]

@app.get("/api/projects/{project_id}/collaborations", response_model=list[CollaborationResponse])
async def get_project_collaborations(project_id: int,current_user: dict = Depends(get_current_user)):
    project = db.execute_query(
        "SELECT * FROM projects WHERE proj_id = %s AND is_deleted = 0",
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
        "SELECT * FROM projects WHERE proj_id = %s",
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

@app.get("/api/collaborations/me")
async def get_my_collaborations(current_user: dict = Depends(get_current_user)):
    """Fetch all collaboration requests - both outgoing (user requested) and incoming (projects they own)."""
    
    # 1. Outgoing: Requests the user has sent to projects
    outgoing = db.execute_query(
        """
        SELECT 
            cr.collab_id,
            cr.project_id,
            cr.user_id,
            cr.message,
            cr.status,
            cr.created_at,
            p.title as project_title,
            u.name as project_owner_name,
            'outgoing' as type
        FROM collaboration_request cr
        JOIN projects p ON cr.project_id = p.proj_id
        JOIN users u ON p.user_id = u.user_id
        WHERE cr.user_id = %s AND cr.is_deleted = 0
        ORDER BY cr.created_at DESC
        """,
        (current_user["user_id"],)
    )
    
    # 2. Incoming: Requests from others for projects the user owns
    incoming = db.execute_query(
        """
        SELECT 
            cr.collab_id,
            cr.project_id,
            cr.user_id,
            cr.message,
            cr.status,
            cr.created_at,
            p.title as project_title,
            u.name as requester_name,
            'incoming' as type
        FROM collaboration_request cr
        JOIN projects p ON cr.project_id = p.proj_id
        JOIN users u ON cr.user_id = u.user_id
        WHERE p.user_id = %s AND cr.is_deleted = 0
        ORDER BY cr.created_at DESC
        """,
        (current_user["user_id"],)
    )
    
    result = []
    if outgoing:
        result.extend(outgoing)
    if incoming:
        result.extend(incoming)
    
    return result or []


# ============================================================================
# Celebration Wall API
# ============================================================================

@app.get("/api/celebrations", response_model=list[CelebrationResponse])
async def get_celebration_wall():
    """Fetch recently completed projects for the celebration wall with comments and collaborators."""
    
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
        FROM projects p
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
    
    # Enrich each celebration with comments and collaborators
    enriched_celebrations = []
    for celebration in celebrations:
        proj_id = celebration['proj_id']
        
        # Fetch all comments from all updates for this project
        comments_data = db.execute_query(
            """
            SELECT 
                c.com_id,
                c.content,
                c.user_id,
                u.name as author_name,
                c.created_at
            FROM comment c
            JOIN updates up ON c.update_id = up.update_id
            JOIN users u ON c.user_id = u.user_id
            WHERE up.project_id = %s AND c.is_deleted = 0
            ORDER BY c.created_at DESC
            LIMIT 5
            """,
            (proj_id,)
        )
        
        # Fetch all collaborators (accepted collaboration requests)
        collaborators_data = db.execute_query(
            """
            SELECT DISTINCT
                u.user_id,
                u.name
            FROM collaboration_request cr
            JOIN users u ON cr.user_id = u.user_id
            WHERE cr.project_id = %s AND cr.status = 'Accepted' AND cr.is_deleted = 0
            """,
            (proj_id,)
        )
        
        celebration['comments'] = comments_data or []
        celebration['collaborators'] = collaborators_data or []
        enriched_celebrations.append(celebration)
    
    return enriched_celebrations