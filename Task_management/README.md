<<<<<<< HEAD
# Task_management
=======
# 🚀 Task Management System API

## 📋 Project Overview

A **lightweight Task Management System API** built with **FastAPI** and **SQLAlchemy** that provides comprehensive project and task management capabilities with real-time email notifications and background job processing.

### ✨ **Key Features**
- 🏗️ **Project & Task Management** - Create, manage, and organize projects with tasks
- 👥 **User Assignment** - Assign tasks to team members with role-based access
- 🔍 **Advanced Filtering** - Filter, sort, and paginate tasks by status, priority, due date
- 📧 **Automatic Email Notifications** - Real-time notifications for task assignments and updates
- ⚡ **Background Processing** - Asynchronous email sending and daily summaries
- 🔐 **JWT Authentication** - Secure token-based authentication with role management
- 🐳 **Docker Ready** - Production-ready containerization
- 🌐 **Cloud Deployable** - Ready for deployment on any cloud platform

---

## What Was Built

### 1. Projects & Tasks

- **Projects:** Can have multiple tasks.  
- **Tasks:** Belong to a project and can be assigned to a user.

---

## API Endpoints Explanation

### Projects

- **POST /projects/**  
  **Requirement:** Create a new project.  
  **What was done:**  
  Authenticated users with role `team_lead` can create projects linked to them.

- **GET /projects/**  
  **Requirement:** List all projects for the authenticated user.  
  **What was done:**  
  Returns all projects owned by the current user.

- **GET /projects/{id}**  
  **Requirement:** Get project details including all tasks.  
  **What was done:**  
  Returns project info and its tasks if the project is owned by the user.

- **PATCH /projects/{id}**  
  **Requirement:** Partially update a project.  
  **What was done:**  
  Allows project owner to update project fields.

- **DELETE /projects/{id}**  
  **Requirement:** Delete a project.  
  **What was done:**  
  Allows project owner to delete the project.

---

### Tasks

- **POST /tasks/**  
  **Requirement:** Create a task under a project and assign it.  
  **What was done:**  
  Project owners/team leads can create tasks and assign them. An email notification is sent asynchronously on assignment.

- **GET /tasks/**  
  **Requirement:** List tasks with filtering, sorting, and pagination.  
  **What was done:**  
  Supports filters (status, priority, due_date, project_id), sorting, pagination. Developers see only assigned tasks, team leads see all.

- **GET /tasks/{id}**  
  **Requirement:** Get task details including project and assigned user.  
  **What was done:**  
  Returns task info if the user is authorized.

- **PATCH /tasks/{id}**  
  **Requirement:** Partially update a task.  
  **What was done:**  
  Allows update of task fields. Sends email if assignment or status changes.

- **PUT /tasks/{id}**  
  **Requirement:** Fully update a task.  
  **What was done:**  
  Replaces task data, with validation and email notifications on status or assignment change.

- **DELETE /tasks/{id}**  
  **Requirement:** Delete a task.  
  **What was done:**  
  Authorized users (team leads) can delete tasks.

---

### Authentication

- **POST /users/register**  
  **Requirement:** User registration with role assignment.  
  **What was done:**  
  Registers users with secure password hashing.

- **POST /users/login**  
  **Requirement:** Authenticate and get JWT token.  
  **What was done:**  
  Returns JWT token to be used in protected endpoints.

---

## 📧 **Email System (UPDATED)**

**✅ Fully Automatic Email Notifications:*
- ✅ **Task assignment emails** - Sent immediately when task assigned
- ✅ **Due date reminders** - Daily at 9 AM for tasks due today/tomorrow
- ✅ **Overdue notifications** - Daily reminders until task completed
- ✅ **Background email processing** - Non-blocking email queue

**Email Triggers:**
- **Task Assignment** → Immediate email to assigned user
- **Due Today** → Morning reminder (9 AM daily)
- **Due Tomorrow** → Advance warning (9 AM daily)  
- **Overdue Tasks** → Daily urgent reminders (9 AM daily)
- **Status Changes** → Immediate notification to assigned user
- **Task Reassignment** → Emails to old and new assignees

**Development Mode:** Emails are logged to console and `email_logs/sent_emails.json`

---

## Tech Stack

- **Framework:** FastAPI  
- **Database:** MySQL  
- **ORM:** SQLAlchemy  
- **Email:** SMTP (configurable via environment variables)  
- **Background tasks:** Python threading with queue for async email sending  
- **Containerization:** Docker (optional)

---

## Local Setup Instructions

1. **Clone the repository:**  
   ```bash
   git clone <repository-url>
   cd Task_management


# Setup Instructions

## Create and activate a virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate   # Linux/Mac
.venv\Scripts\activate      # Windows

pip install -r requirements.txt

Set environment variables:
Create a .env file in the root directory with the following content:

MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=yourpassword
MYSQL_DB=taskdb

SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASS=your-app-password

SECRET_KEY=your-secret-key


Start the FastAPI application:

uvicorn main:app --reload

Database Schema Diagram (Mermaid):
erDiagram
    USER {
        int id PK
        string email
        string password
        string role
    }
    PROJECT {
        int id PK
        string title
        string description
        int owner_id FK
    }
    TASK {
        int id PK
        string title
        string description
        string priority
        datetime due_date
        bool completed
        int assigned_user_id FK
        int project_id FK
        string status
    }
    USER ||--o{ PROJECT : owns
    USER ||--o{ TASK : assigned_to
    PROJECT ||--o{ TASK : contains

Sample cURL Requests:(register user, login user, create project, create task, list task)

curl -X POST "http://localhost:8000/users/register" -H "Content-Type: application/json" -d '{"email":"user@example.com","password":"yourpassword","role":"team_lead"}'


curl -X POST "http://localhost:8000/users/login" -H "Content-Type: application/json" -d '{"email":"user@example.com","password":"yourpassword"}'


curl -X POST "http://localhost:8000/projects/" -H "Authorization: Bearer <token>" -H "Content-Type: application/json" -d '{"title":"Project Alpha","description":"First project"}'


curl -X POST "http://localhost:8000/tasks/?role=team_lead&user_id=1" -H "Authorization: Bearer <token>" -H "Content-Type: application/json" -d '{"title":"Initial Task","description":"Do something important","priority":"high","due_date":"2025-08-15","project_id":1,"assigned_user_id":2}'


curl -X GET "http://localhost:8000/tasks/?status=pending&priority=high&sort_by=due_date&skip=0&limit=5" -H "Authorization: Bearer <token>"
>>>>>>> 02b8c0d (Initial commit)
