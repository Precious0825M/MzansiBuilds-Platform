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

### DELETE /api/projects/:proj_id
Delete a project.

#### How
+ Removes a project from the system, will be restricted to the owner (might consider have a bolean value they can update, if True then project will not show for the user)

## 4. Update APIs (For Progress Tracking)

### POST /api/updates
Create a progress update for a project.

#### How
+ Inserts a new record into the Update table
+ Links update to both project_id and user_id

### GET /api/updates
Retrieve all updates (For Live Feed).

#### How
+ Returns updates across all projects
+ Ordered by created_at (latest first)

### GET /api/projects/:proj_id/updates
Retrieve updates for a specific project.

#### How
+ Filters updates using project_id
+ Displays project-specific progress history

### DELETE /api/updates/:update_id
Delete an update.

#### How 
+ Removes an update from the system -- Will update the DB to have an isDelete boolean if True the update will not be shown
+ Restricted to the creator

## 5. Comment APIs

### POST /api/comments
For adding a comment to an update.

#### How
+ Inserts a record into the Comment table
+ Links comment to update_id and user_id

### GET /api/updates/:update_id/comments
Retrieve comments for a specific update.

#### How
+ Returns all comments linked to an update

### DELETE /api/comments/:com_id
Delete a comment.

#### How
+ Removes a comment -- Will update the schema to have isDeleted boolean, when True the comment will not show
+ Restricted to the user who wrote the comment

## 6. Collaboration Request APIs

### POST /api/collaborations
Raise a collaboration request (raise a hand).

#### How
+ Creates a new CollaborationRequest
+ Links project_id(The project they want to collaborate on) and user_id(The user who wishes to collaborate)
+ Stores optional message explaining how they will collaborate

### GET /api/projects/:proj_id/collaborations
View collaboration requests for a project.

#### How
+ Retrieves all requests for a specific project -- Allows project owner to review requests

### PATCH /api/collaborations/:collab_ID
Update collaboration request status.

#### How
+ Updates status and updated_at
+ Restricted to project owner

## 7. Celebration Wall API

### GET /api/celebrations
Retrieve completed projects -- Used to display the Celebration Wall

#### How
+ Returns projects where: stage = 'Completed'


## Authorisation Notes

### Protected routes require authentication:
+ Creating projects
+ Posting updates
+ Commenting
+ Raising collaboration requests

### Ownership checks should be enforced:
+ Only project owners can edit/delete projects
+ Only creators can delete their updates/comments
+ Only project owners can accept/reject collaboration requests
