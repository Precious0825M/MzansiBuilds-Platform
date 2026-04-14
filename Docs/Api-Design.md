# MzansiBuilds- API Design

This document outlines the API structure for the MzansiBuilds platform. The API is designed using RESTful principles and maps directly to the database schema.

## 1. Authentication APIs

### POST /api/auth/register
This is meant to register new users.

#### How
+ It accepts user details (name,email,password, ...)
+ Hashes the password before storing
+ creates a new record in the User table

### POST /api/auth/login 
meant to authenticate an existing user.

#### How
+ Verifies email and password
+ Returns authentication token/session
+ Grants access to protected routes

### GET /api/auth/me
Retrieves the curent logged in user.

#### How
+ Uses the token/session to identify the user
+ returns the user details


## 2. User APIs

### GET /api/users/:id
Fetches a specific user's profile.

#### How 
+ Retrieves user information from the User table
+ Can be used to view other developers

### PUT /api/users/
Update user profile.

#### How
+ Allows user to update fields like name or bio
+ Updates updated_at timestamp

## 3. Project APIs

### POST /api/projects
Meant to create new projct

#### How
+ Inserts a new record into the Project table
+ Links project to the logged-in user via user_id

### GET /api/projects
Retrieve all projects.

#### How
+ Returns a list of projects
+ Used to display available projects across the platform

### GET /api/projects/:id
Retrieve a single project.

#### How
+ Fetches detailed information about one project

### GET /api/projects/user/:user_id
Retrieve projects created by a specific user.

#### How
+ Returns projects filtered using user_id


### PUT /api/projects/:proj_id
Update a project.

#### How
+ Allows project owner to edit: title, description, stage, support_needed
+ Updates the updated_at timestamp
+ Stage transitions: Planning → Development → Testing → Completed
+ Permission: Only project owner can update

### DELETE /api/projects/:proj_id
Delete a project (soft delete).

#### How
+ Sets is_deleted = True instead of removing the record
+ Project no longer appears in project listings
+ Permission: Restricted to the project owner
+ Preserves project history and audit trail

## 4. Update APIs (For Progress Tracking)

### POST /api/updates
Create a progress update for a project.

#### How
+ Inserts a new record into the Update table
+ Links update to both project_id and user_id
+ Sets is_deleted to False by default

### GET /api/updates
Retrieve all updates (For Live Feed).

#### How
+ Returns updates across all projects ordered by created_at (latest first)
+ **Enriched Response includes:**
  - Project details (title, description, stage)
  - Project owner information (name, email)
  - Update author information (name, bio)
  - Nested comments array with author names
  - Current user's collaboration request status (if any)
  - Flag indicating if current user is project owner
+ Filters out soft-deleted updates (is_deleted = False)

### GET /api/projects/:proj_id/updates
Retrieve updates for a specific project.

#### How
+ Filters updates using project_id
+ Displays project-specific progress history
+ Excludes soft-deleted updates

### DELETE /api/updates/:update_id
Delete an update (soft delete).

#### How 
+ Sets is_deleted = True instead of removing the record
+ Preserves audit trail
+ Permission: Restricted to the creator of the update

## 5. Comment APIs

### POST /api/comments
For adding a comment to an update.

#### How
+ Inserts a record into the Comment table
+ Links comment to update_id and user_id
+ Sets is_deleted to False by default

### GET /api/updates/:update_id/comments
Retrieve comments for a specific update.

#### How
+ Returns all comments linked to an update
+ Includes comment author name and details
+ Excludes soft-deleted comments (is_deleted = False)
+ Comments are nested within update responses when using GET /api/updates

### DELETE /api/comments/:com_id
Delete a comment (soft delete).

#### How
+ Sets is_deleted = True instead of removing the record
+ Preserves audit trail
+ Permission: Restricted to the user who wrote the comment

## 6. Collaboration Request APIs

### POST /api/collaborations
Raise a collaboration request (raise a hand).

#### How
+ Creates a new CollaborationRequest
+ Links project_id (the project to collaborate on) and user_id (the person requesting)
+ Stores optional message explaining collaboration intent
+ Sets status to 'Pending' by default
+ Permission: Non-owners only (prevents project owner from requesting on their own project)

### GET /api/projects/:proj_id/collaborations
View collaboration requests for a project.

#### How
+ Retrieves all requests for a specific project
+ Allows project owner to review pending requests
+ Permission: Restricted to project owner

### GET /api/collaborations/me
Retrieve collaboration requests for current user.

#### How
+ Returns both **incoming requests** (for projects user owns) and **outgoing requests** (user initiated)
+ Each request includes type field ('incoming' or 'outgoing')
+ Shows requester/project details and current status
+ Useful for dashboard to show notifications like "2 updates shared"

### PATCH /api/collaborations/:collab_id
Update collaboration request status.

#### How
+ Updates status: Pending → Accepted or Pending → Rejected
+ Updates the updated_at timestamp
+ Permission: Restricted to project owner
+ Only status field can be updated

## 7. Celebration Wall API

### GET /api/celebrations
Retrieve completed projects for the Celebration Wall.

#### How
+ Returns projects where stage = 'Completed'
+ **Enriched Response includes:**
  - Project details (title, description, owner name)
  - Comments array: up to 5 most recent comments with author names
  - Collaborators array: all users with 'Accepted' collaboration requests on this project
+ Each comment includes: author_name, content, creation date
+ Each collaborator includes: user_name, bio
+ Ordered by project completion date (latest first)


## Authorization & Security

### Authentication
+ All protected routes require valid JWT token in Authorization header
+ Token obtained from POST /api/auth/login
+ Token stored in localStorage on frontend

### Protected Routes (Require Authentication)
+ Creating projects: POST /api/projects
+ Creating updates: POST /api/updates
+ Commenting: POST /api/comments
+ Raising collaboration requests: POST /api/collaborations
+ Updating user profile: PUT /api/users/

### Permission Checks (Authorization)
+ **Project ownership:** Only project owner can update/delete project, change stage
+ **Update/Comment creation:** Only creator can delete their own updates/comments
+ **Collaboration requests:** Only project owner can accept/reject requests
+ **Collaboration self-request:** Non-owners only (users can't request on their own projects)

### Soft Deletes
+ All deletions set is_deleted = True rather than hard delete
+ Ensures audit trail, data recovery, and referential integrity
+ Queries automatically filter out soft-deleted records (is_deleted = False)
+ Applies to: Projects, Updates, Comments, CollaborationRequests, Users
