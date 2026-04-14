"""
Seed Data Script for MzansiBuilds
This script populates the database with realistic sample data.
- 5 users with profiles
- 5 projects per user (25 total)
- Multiple updates and collaborations per project
- Mix of project stages
"""

import os
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from app.db.database import db_config
from app.core.security import hash_password


# Sample user data
USERS_DATA = [
    {
        "name": "Amadi Okafor",
        "email": "amadi.okafor@mzansi.dev",
        "password": "SecurePass123!",
        "bio": "Full-stack developer passionate about African tech innovation",
    },
    {
        "name": "Zara Mthembu",
        "email": "zara.mthembu@mzansi.dev",
        "password": "SecurePass123!",
        "bio": "UI/UX Designer and Frontend specialist",
    },
    {
        "name": "Kwame Asante",
        "email": "kwame.asante@mzansi.dev",
        "password": "SecurePass123!",
        "bio": "DevOps and Cloud Infrastructure Engineer",
    },
    {
        "name": "Naledi Dlamini",
        "email": "naledi.dlamini@mzansi.dev",
        "password": "SecurePass123!",
        "bio": "Product Manager and Business Analyst",
    },
    {
        "name": "Chukwu Nwosu",
        "email": "chukwu.nwosu@mzansi.dev",
        "password": "SecurePass123!",
        "bio": "Backend engineer and database specialist",
    },
]

# Sample projects data
PROJECTS_DATA = {
    "Amadi Okafor": [
        {
            "title": "AI-Powered Agriculture Platform",
            "description": "Mobile app that uses AI to help farmers optimize crop yields and predict weather patterns",
            "stage": "Development",
            "support_needed": "Mobile developer, ML engineer",
        },
        {
            "title": "Community Marketplace",
            "description": "E-commerce platform for African artisans to sell handmade crafts globally",
            "stage": "Testing",
            "support_needed": "Quality assurance, payment integration",
        },
        {
            "title": "Educational Content Hub",
            "description": "Platform for creating and sharing educational content with offline functionality",
            "stage": "Completed",
            "support_needed": None,
        },
        {
            "title": "Healthcare Booking System",
            "description": "Telemedicine platform connecting patients with healthcare providers in remote areas",
            "stage": "Planning",
            "support_needed": "Healthcare consultant, compliance expert",
        },
        {
            "title": "Supply Chain Tracker",
            "description": "Blockchain-based supply chain transparency for manufacturing",
            "stage": "Development",
            "support_needed": "Blockchain developer",
        },
    ],
    "Zara Mthembu": [
        {
            "title": "Design System Library",
            "description": "Comprehensive design system and component library for African tech startups",
            "stage": "Completed",
            "support_needed": None,
        },
        {
            "title": "Accessibility Audit Tool",
            "description": "Web app to audit and improve digital accessibility for WCAG compliance",
            "stage": "Development",
            "support_needed": "QA tester, accessibility expert",
        },
        {
            "title": "Event Management Dashboard",
            "description": "Admin dashboard for managing large-scale community events",
            "stage": "Testing",
            "support_needed": "Backend developer",
        },
        {
            "title": "Mobile Banking Interface",
            "description": "Modern UI redesign for a fintech application",
            "stage": "Planning",
            "support_needed": "Fintech specialist, backend integration",
        },
        {
            "title": "Social Learning Platform",
            "description": "Collaborative learning platform with real-time features",
            "stage": "Development",
            "support_needed": "Backend developer, DevOps",
        },
    ],
    "Kwame Asante": [
        {
            "title": "Kubernetes Migration Project",
            "description": "Migrate legacy monolithic application to Kubernetes microservices",
            "stage": "Development",
            "support_needed": "Backend architect, SRE",
        },
        {
            "title": "CI/CD Pipeline Automation",
            "description": "Automated deployment pipeline for multiple environments",
            "stage": "Completed",
            "support_needed": None,
        },
        {
            "title": "Infrastructure as Code",
            "description": "Terraform modules for cloud infrastructure standardization",
            "stage": "Testing",
            "support_needed": "Cloud architect",
        },
        {
            "title": "Disaster Recovery Plan",
            "description": "Comprehensive DR and backup strategy implementation",
            "stage": "Planning",
            "support_needed": "Security expert, database admin",
        },
        {
            "title": "Cloud Cost Optimization",
            "description": "Analyze and reduce cloud infrastructure costs by 40%",
            "stage": "Development",
            "support_needed": "Financial analyst",
        },
    ],
    "Naledi Dlamini": [
        {
            "title": "Market Research Analytics",
            "description": "Data analytics platform for African market research",
            "stage": "Completed",
            "support_needed": None,
        },
        {
            "title": "User Feedback System",
            "description": "Centralized platform for collecting and analyzing user feedback",
            "stage": "Development",
            "support_needed": "Frontend developer, data analyst",
        },
        {
            "title": "Product Roadmap Tracker",
            "description": "Project management tool specifically for product development",
            "stage": "Testing",
            "support_needed": "UX designer, backend developer",
        },
        {
            "title": "Business Intelligence Dashboard",
            "description": "Executive dashboard for real-time business metrics",
            "stage": "Planning",
            "support_needed": "Data scientist, designer",
        },
        {
            "title": "Customer Success Platform",
            "description": "End-to-end customer management and engagement tool",
            "stage": "Development",
            "support_needed": "Full-stack developer",
        },
    ],
    "Chukwu Nwosu": [
        {
            "title": "Real-time Analytics Engine",
            "description": "High-performance analytics engine processing millions of events",
            "stage": "Development",
            "support_needed": "Data engineer, DevOps",
        },
        {
            "title": "Database Optimization",
            "description": "Query optimization and indexing strategy for multi-tenant database",
            "stage": "Completed",
            "support_needed": None,
        },
        {
            "title": "API Gateway Development",
            "description": "Custom API gateway with rate limiting and authentication",
            "stage": "Testing",
            "support_needed": "Security specialist",
        },
        {
            "title": "Data Migration Tool",
            "description": "Automated tool for migrating data between database systems",
            "stage": "Planning",
            "support_needed": "SQL expert, data engineer",
        },
        {
            "title": "Cache Management System",
            "description": "Distributed caching solution for improved performance",
            "stage": "Development",
            "support_needed": "Infrastructure engineer",
        },
    ],
}

# Sample project updates
PROJECT_UPDATES = {
    1: [
        "Started initial research on AI models for crop prediction",
        "Completed data collection from 100 farmers in pilot region",
        "Built first prototype of weather prediction module",
        "Integrated with satellite imagery API for real-time monitoring",
    ],
    2: [
        "Launched beta version with 50 artisan partners",
        "Integrated Stripe payment gateway",
        "User testing revealed good feedback on checkout flow",
        "Fixed mobile responsiveness issues",
    ],
    3: [
        "Project launched successfully with 1000+ downloads",
        "Received positive feedback from educational institutions",
        "Achieved 95% offline functionality rating",
    ],
    5: [
        "Completed requirements gathering with stakeholders",
        "Smart contract development in progress",
        "Testing blockchain integration with supply chain partners",
    ],
    6: [
        "Design system now includes 150+ components",
        "Published documentation and usage guidelines",
        "Used by 5 startups in their products",
    ],
    8: [
        "Completed WCAG 2.1 AA compliance testing",
        "Integrated with Chrome DevTools for real-time auditing",
        "Dashboard shows detailed accessibility insights",
    ],
    10: [
        "Started design phase with stakeholder meetings",
        "Initial wireframes approved by leadership",
    ],
    11: [
        "Successfully migrated 60% of services to Kubernetes",
        "Reduced deployment time from 2 hours to 15 minutes",
        "Performance improved by 35%",
    ],
    12: [
        "Pipeline deployed and tested in production",
        "Automated test coverage increased to 85%",
        "Developers report 50% reduction in deployment issues",
    ],
    14: [
        "Completed all backend infrastructure setup",
        "Scheduled security audit for next milestone",
    ],
    16: [
        "Alpha version complete with 10 analytics modules",
        "Successfully processing 100k events per second",
        "User testing phase scheduled for next sprint",
    ],
    17: [
        "Successfully optimized 50 critical queries",
        "Added 200+ new indexes",
        "Query performance improved by 70%",
    ],
    19: [
        "API gateway deployed to staging environment",
        "Authentication module tested and working",
        "Rate limiting configured and validated",
    ],
}

# Sample collaboration requests
COLLABORATION_REQUESTS = [
    {"project_id": 1, "requester_idx": 1, "status": "Accepted", "message": "I'm interested in UI design for the farmer interface"},
    {"project_id": 1, "requester_idx": 2, "status": "Pending", "message": "Can I help with infrastructure setup?"},
    {"project_id": 2, "requester_idx": 2, "status": "Accepted", "message": "Let me help with the payment flow design"},
    {"project_id": 3, "requester_idx": 3, "status": "Accepted", "message": "I can help optimize the offline sync"},
    {"project_id": 5, "requester_idx": 4, "status": "Pending", "message": "Interested in contributing to supply chain module"},
    {"project_id": 6, "requester_idx": 0, "status": "Accepted", "message": "Can I contribute component documentation?"},
    {"project_id": 8, "requester_idx": 1, "status": "Accepted", "message": "Let's collaborate on the audit engine"},
    {"project_id": 11, "requester_idx": 3, "status": "Accepted", "message": "I want to help with migration strategy"},
    {"project_id": 12, "requester_idx": 4, "status": "Pending", "message": "Can I review the CI/CD configuration?"},
    {"project_id": 16, "requester_idx": 2, "status": "Accepted", "message": "I'd like to work on data pipeline optimization"},
    {"project_id": 17, "requester_idx": 1, "status": "Pending", "message": "Interested in contributing to performance testing"},
    {"project_id": 19, "requester_idx": 0, "status": "Accepted", "message": "Let me help implement authentication"},
]

# Sample comments on updates
COMMENT_DATA = {
    1: [
        {
            "update_id": 1,
            "commenter_idx": 1,
            "content": "Great progress! How are you handling privacy concerns with farmer data?",
        },
        {
            "update_id": 1,
            "commenter_idx": 2,
            "content": "The satellite integration is impressive. What resolution are you targeting?",
        },
    ],
    2: [
        {
            "update_id": 5,
            "commenter_idx": 0,
            "content": "Impressive beta metrics! What's the conversion rate so far?",
        },
    ],
    5: [
        {
            "update_id": 18,
            "commenter_idx": 3,
            "content": "The smart contract approach is innovative. Have you considered security audits?",
        },
    ],
    11: [
        {
            "update_id": 36,
            "commenter_idx": 4,
            "content": "35% performance improvement is exceptional! What was the main bottleneck?",
        },
    ],
}


def seed_database():
    """Populate the database with seed data."""
    try:
        print(" Starting database seeding...")

        # Create users
        print("\n Creating users...")
        user_ids = {}
        for user_data in USERS_DATA:
            user_query = '''
                INSERT INTO users (name, email, password_hash, bio)
                VALUES (%s, %s, %s, %s)
            '''
            hashed_password = hash_password(user_data["password"])
            user_id = db_config.execute_insert(
                user_query,
                (
                    user_data["name"],
                    user_data["email"],
                    hashed_password,
                    user_data["bio"],
                ),
            )
            user_ids[user_data["name"]] = user_id
            print(f"  ✓ Created user: {user_data['name']} (ID: {user_id})")

        # Create projects
        print("\n Creating projects...")
        project_ids = {}
        project_counter = 1
        for user_name, projects in PROJECTS_DATA.items():
            user_id = user_ids[user_name]
            for project_data in projects:
                project_query = '''
                    INSERT INTO projects (user_id, title, description, stage, support_needed)
                    VALUES (%s, %s, %s, %s, %s)
                '''
                project_id = db_config.execute_insert(
                    project_query,
                    (
                        user_id,
                        project_data["title"],
                        project_data["description"],
                        project_data["stage"],
                        project_data["support_needed"],
                    ),
                )
                project_ids[project_counter] = {
                    "id": project_id,
                    "user_id": user_id,
                    "title": project_data["title"],
                }
                print(
                    f"  ✓ Created project: {project_data['title']} (ID: {project_id}, Owner: {user_name})"
                )
                project_counter += 1

        # Create updates
        print("\n Creating project updates...")
        update_counter = 1
        for project_num, updates in PROJECT_UPDATES.items():
            project_info = project_ids.get(project_num)
            if not project_info:
                continue

            for update_text in updates:
                # Create update with random past dates
                days_ago = len(updates) - updates.index(update_text)
                created_at = datetime.utcnow() - timedelta(days=days_ago, hours=8)

                update_query = '''
                    INSERT INTO updates (project_id, user_id, content, created_at)
                    VALUES (%s, %s, %s, %s)
                '''
                update_id = db_config.execute_insert(
                    update_query,
                    (
                        project_info["id"],
                        project_info["user_id"],
                        update_text,
                        created_at,
                    ),
                )
                print(
                    f"  ✓ Created update for '{project_info['title']}' (Update ID: {update_id})"
                )
                update_counter += 1

        # Create collaboration requests
        print("\n Creating collaboration requests...")
        all_user_names = list(user_ids.keys())
        user_id_list = [user_ids[name] for name in all_user_names]

        for collab_data in COLLABORATION_REQUESTS:
            project_info = project_ids.get(collab_data["project_id"])
            if not project_info:
                continue

            requester_id = user_id_list[collab_data["requester_idx"]]

            # Don't create self-collaboration
            if requester_id == project_info["user_id"]:
                continue

            collab_query = '''
                INSERT INTO collaboration_request (project_id, user_id, message, status)
                VALUES (%s, %s, %s, %s)
            '''
            collab_id = db_config.execute_insert(
                collab_query,
                (
                    project_info["id"],
                    requester_id,
                    collab_data["message"],
                    collab_data["status"],
                ),
            )
            requester_name = all_user_names[collab_data["requester_idx"]]
            print(
                f"  ✓ Created collaboration request: {requester_name} → '{project_info['title']}' ({collab_data['status']})"
            )

        # Create comments on updates
        print("\n Creating comments on updates...")
        update_id_counter = 1
        for project_num, comments_list in COMMENT_DATA.items():
            project_info = project_ids.get(project_num)
            if not project_info:
                continue

            for comment_data in comments_list:
                commenter_id = user_id_list[comment_data["commenter_idx"]]

                comment_query = '''
                    INSERT INTO comment (update_id, user_id, content)
                    VALUES (%s, %s, %s)
                '''
                comment_id = db_config.execute_insert(
                    comment_query,
                    (
                        comment_data["update_id"],
                        commenter_id,
                        comment_data["content"],
                    ),
                )
                commenter_name = all_user_names[comment_data["commenter_idx"]]
                print(f"  ✓ Created comment by {commenter_name} (Comment ID: {comment_id})")

        print("\n" + "=" * 60)
        print(" Database seeding completed successfully!")
        print("=" * 60)
        print("\n Summary:")
        print(f"   • Users created: {len(USERS_DATA)}")
        print(f"   • Projects created: {len(project_ids)}")
        print(f"   • Updates created: {update_counter - 1}")
        print(f"   • Collaborations created: {len(COLLABORATION_REQUESTS)}")
        print("\n Test Credentials:")
        for user in USERS_DATA:
            print(f"   • Email: {user['email']} | Password: {user['password']}")

    except Exception as e:
        print(f" Error seeding database: {str(e)}")
        raise


if __name__ == "__main__":
    seed_database()
