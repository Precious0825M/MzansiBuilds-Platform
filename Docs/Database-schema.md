# MzansiBuilds- Database Schema Design

This document outlines the design for the MzansiBuilds database. We prioritize simplicity while addressing all requirements, and the design considers future scalability.

## Design Principles

### Soft Delete Strategy
All entities use soft deletes with an `is_deleted` flag instead of hard deletion:
- When `is_deleted = False`, the record is active and visible in queries
- When `is_deleted = True`, the record is hidden but preserved in the database
- Benefits: Audit trail, data recovery, referential integrity, compliance

### Timestamps
Every entity has `created_at` and `updated_at` timestamps for:
- Audit trail: tracking when records are created/modified
- Reporting: analyzing platform activity over time
- User reminders: notifying owners of pending actions

##
## Entities

### 1. User
Represents a developer using the platform.

#### Fields:

+ user_id (Primary key)
+ name
+ email (must be unique)
+ password (must be hashed)
+ bio
+ is_deleted -- Incase user wants to delete their account
+ created_at (Might be used for rporting later)
+ updated_at (Also for future reports) -- Can help us remind the user when they last changed their information


### 2. Project
Represents a developer's project.

#### Fields:

+ proj_id (Primary key)
+ user_id (Foreign Key) -- to track who owns the project
+ title
+ description
+ stage(ENUM: Planing, Development, Testing, Completed) -- This to keep track of where the project is at in its lifespan.
+ support_needed -- The developer can use this to let others know he needs help.
+ is_deleted
+ created_at
+ updated_at

### 3. Update
Represents progress updates or milestones for a project.

#### Fields:

+ update_id (Primary key)
+ project_id (Foreign Key) -- which project was updated 
+ user_id (Foreign Key) -- who made the update
+ content -- What exactly was the update about
+ created_at -- tells us when the update was made
+ is_deleted -- soft delete flag; when True, update is hidden from queries
+ updated_at -- updated timestamp for audit tracking


### 4. Comment
Represents user interaction on updates, bringing a little sociality to the platform

#### Fields:

+ com_id (Primary key) 
+ update_id (Foreign Key) -- which update was the comment on 
+ user_id (Foreign Key) -- who made the comment
+ content -- what was the comment 
+ created_at -- when was the comment made
+ is_deleted -- soft delete flag; when True, comment is hidden from queries
+ updated_at -- updated timestamp for audit tracking


### 5. CollaborationRequest
Represents a request by a user to collaborate on a project or to offer the needed support

#### Fields:

+ collab_id (Primary key)
+ project_id (Foreign Key) -- which project to collaborate on
+ user_id (Foreign Key) -- who wants to collaborate (the requester, not the project owner)
+ message -- optional details on how they want to collaborate 
+ status (ENUM: Pending, Accepted, Rejected) -- owner decides if they want to accept/reject
+ is_deleted -- soft delete flag; when True, request is hidden from queries
+ created_at -- when the request was made (useful for reminding owners after periods)
+ updated_at -- when the owner actually responded

### Relationships
+ A User can have many Projects (one-to-many)
+ A Project belongs to one User (many-to-one: the owner)
+ A Project can have many Updates (one-to-many)
+ An Update belongs to one Project (many-to-one)
+ A User can create many Updates (one-to-many)
+ An Update can have many Comments (one-to-many)
+ A User can create many Comments (one-to-many)
+ A Project can have many CollaborationRequests (one-to-many)
+ A User can create many CollaborationRequests (one-to-many: the requester)

### Query Patterns
All queries filter by `is_deleted = False` to exclude soft-deleted records:
- Dashboard Live Feed: `WHERE is_deleted = False ORDER BY created_at DESC`
- Celebration Wall: `WHERE stage = 'Completed' AND is_deleted = False`
- User Projects: `WHERE user_id = X AND is_deleted = False`
- Project Updates: `WHERE project_id = X AND is_deleted = False`
- Update Comments: `WHERE update_id = X AND is_deleted = False`
