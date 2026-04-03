# MzansiBuilds- Database Schema Design

This document outlines the design for the MzansiBuilds database. We prioritize simplicity while addressing all requirements, and the design considers future scalability.
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
+ is_deleted


### 4. Comment
Represents user interaction on updates, bringing a little sociality to the platform

#### Fields:

+ com_id (Primary key) 
+ update_id (Foreign Key) -- which update was the comment on 
+ user_id (Foreign Key) -- who made the comment
+ content -- what was the comment 
+ created_at -- when was the comment made
+ is_deleted


### 5. CollaborationRequest
Represents a request by a user to collaborate on a project or to offer the needed support

#### Fields:

+ collab_id (Primary key)
+ project_id (Foreign Key) -- Tells us which project
+ user_id (Foreign Key) -- Tells us who wants to collaborate (We already know who owns the project)
+ message -- User can give details on how they want to collaborate 
+ status(ENUM: Pending, Accepted, Rejected) -- Owner can decide if they want to accept or not
+ is_deleted -- Incase user wants to lower their hand for collaboration 
+ created_at -- Tells us when was the request made(We can use this to remind owners after certain periods) 
+ Update_at -- This will tell us when the owner actually responded

### Relationships
+ A User can have many Projects
+ A Project belongs to one User
+ A Project can have many Updates
+ An Update belongs to one Project
+ A User can create many Updates
+ An Update can have many Comments
+ A User can create many Comments
+ A Project can have many CollaborationRequests
+ A User can create many CollaborationRequests
