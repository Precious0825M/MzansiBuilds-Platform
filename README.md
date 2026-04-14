# MzansiBuilds-Platform

A collaborative platform that empowers developers to **build in public**, **share their progress**, and **collaborate with peers**. MzansiBuilds focuses on transparency, community connection, and celebrating shipped projects.

## What Is MzansiBuilds?

MzansiBuilds is a social platform for developers where you can:
- **Share Your Work**: Post progress updates on your projects in real-time
- **Discover Projects**: See what other developers are building and learning from their journey
- **Collaborate**: Request to collaborate on projects and respond to collaboration requests
- **Engage**: Comment on updates, celebrate completed projects, and build community
- **Track Progress**: Move projects through stages (Planning → Development → Testing → Completed) and celebrate when you ship

## Key Features

### Live Feed
See real-time updates from developers across the platform. Comment on updates and request to collaborate on projects that interest you.

### Collaboration System
- Send collaboration requests to projects you want to help with
- As a project owner, review and accept/decline requests
- Track your incoming collaboration requests and outgoing requests on your dashboard

### Celebration Wall
View completed projects with their journey, comments, and the team members who helped ship them. Celebrate your wins and inspire others.

### Project Lifecycle
Manage your projects through clear stages:
- **Planning**: Initial ideas and planning phase
- **Development**: Active development work
- **Testing**: Quality assurance and refinement
- **Completed**: Shipped and live (appears on Celebration Wall)

## Tech Stack

### Backend
- **Framework**: FastAPI (Python)
- **Database**: MySQL with soft-delete architecture
- **Authentication**: JWT tokens with password hashing (bcrypt)
- **API Design**: RESTful with enriched data responses

### Frontend
- **Framework**: React with TypeScript
- **Styling**: Tailwind CSS
- **Icons**: React Icons (Font Awesome)
- **State**: React Hooks with localStorage for auth persistence

## Architecture Highlights

### Security
- **Soft Deletes**: All deletions preserve data with `is_deleted` flag for audit trails and recovery
- **Permission Checks**: Only project owners can modify projects; only creators can delete their content
- **Password Hashing**: Bcrypt hashing with passlib
- **JWT Authentication**: Secure token-based auth with expiration
- **Input Validation**: Pydantic models enforce strict type validation on all endpoints

### Data Flow
- Backend enriches API responses with full context (author details, nested comments, collaborators)
- Frontend uses async/await pattern for data fetching with proper error handling
- TypeScript provides compile-time type safety throughout the application

## Project Structure

```
MzansiBuilds-Platform/
├── backend/                 # FastAPI server
│   ├── app/
│   │   ├── main.py         # Main app with all endpoints
│   │   ├── core/           # Auth and security utilities
│   │   ├── db/             # Database configuration
│   │   └── schemas/        # Pydantic validation models
│   └── requirements.txt
├── frontend/               # React TypeScript app
│   ├── src/
│   │   ├── pages/         # Page components
│   │   ├── components/    # Reusable components
│   │   └── api/           # API client
│   └── package.json
└── Docs/                  # Documentation
    ├── Api-Design.md      # API endpoint documentation
    └── Database-schema.md # Database structure
```

## Getting Started

### Prerequisites
- Python 3.10+
- Node.js 16+
- MySQL 8.0+

### Backend Setup
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

### Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

### Running Seed_data --to get data for presentation
```bash
cd backend
python seed_data.py
```

Visit `http://localhost:5173` to access the platform (backend runs on `http://localhost:8000`).

## Documentation

- **[API Design](./Docs/Api-Design.md)** - Complete API endpoint reference with request/response examples and authorization rules
- **[Database Schema](./Docs/Database-schema.md)** - Database design with soft-delete strategy and relationships

## Design Philosophy

**Secure By Design**: Security is built into every layer—from password hashing to permission checks to soft deletes. We don't add security as an afterthought; it's woven into the architecture from day one.

**Developer Experience**: The platform is designed with developers in mind. Simple authentication, clear feedback, and a community that celebrates progress—not just perfection.
