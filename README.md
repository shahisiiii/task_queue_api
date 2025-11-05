# Task Queue & Notification API
A Django REST Framework application with Celery and Redis for managing asynchronous background tasks.

## Features

JWT-based authentication
Asynchronous task processing with Celery
Redis caching for fast data retrieval
Admin-only endpoints
Docker support

## Tech Stack

Backend: Django 4.2, Django REST Framework
Authentication: JWT (Simple JWT)
Task Queue: Celery 5.5
Message Broker: Redis
Database: PostgreSQL
Caching: Redis (django-redis)


## Installation

Option 1: Local Setup
Prerequisites

Python 3.11 
PostgreSQL 15
Redis 7

## Steps

Clone the repository

```bash git clone <repository-url> ```
```bash cd task_queue_project ```

## Create virtual environment

``` bash python -m venv venv ```
``` bash source venv/bin/activate  # On Windows: venv\Scripts\activate ```

## Install dependencies

``` bash pip install -r requirements.txt ```

## Create .env file

``` bash cp .env.example .env ```

Edit .env with your configuration

Setup database

``` bash # Create PostgreSQL database ```
``` bash createdb task_queue_db ```

## Run migrations

``` bash python manage.py makemigrations ```
``` bash python manage.py migrate ```

## Create superuser (optional)

``` bash python manage.py createsuperuser ```

## Start Redis

```bash redis-server```

# Run the application

Open 4 terminal windows:
Terminal 1 - Django Server:
bashpython manage.py runserver
Terminal 2 - Celery Worker:
bashcelery -A task_queue_project worker --pool=solo --loglevel=info
Terminal 3 - Celery Beat (for periodic tasks):
bashcelery -A task_queue_project beat --loglevel=info


The application will be available at http://localhost:8000

# API Endpoints

Authentication
Register User
httpPOST /api/users/register/
Content-Type: application/json

{
  "username": "john_doe",
  "email": "john@example.com",
  "password": "SecurePass123!",
  "password2": "SecurePass123!",
  "first_name": "John",
  "last_name": "Doe"
}
Response:
json{
  "user": {
    "id": 1,
    "username": "john_doe",
    "email": "john@example.com"
  },
  "tokens": {
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...",
    "access": "eyJ0eXAiOiJKV1QiLCJhbGc..."
  },
  "message": "User registered successfully"
}
Login
httpPOST /api/users/login/
Content-Type: application/json

{
  "username": "john_doe",
  "password": "SecurePass123!"
}
Response:
json{
  "user": {
    "id": 1,
    "username": "john_doe",
    "email": "john@example.com"
  },
  "tokens": {
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...",
    "access": "eyJ0eXAiOiJKV1QiLCJhbGc..."
  },
  "message": "Login successful"
}
Refresh Token
httpPOST /api/users/token/refresh/
Content-Type: application/json

{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}

# Tasks

Create Task

httpPOST /api/tasks/tasks/
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "title": "Process Customer Data",
  "description": "Import and process customer CSV file"
}
Response:
json{
  "task": {
    "id": 1,
    "user": {
      "id": 1,
      "username": "john_doe",
      "email": "john@example.com"
    },
    "title": "Process Customer Data",
    "description": "Import and process customer CSV file",
    "status": "PENDING",
    "result": null,
    "celery_task_id": "8f7e2c3d-4b1a-5e6f-7g8h-9i0j1k2l3m4n",
    "created_at": "2025-11-05T10:30:00Z",
    "updated_at": "2025-11-05T10:30:00Z"
  },
  "message": "Task created and processing started"
}

List Tasks

httpGET /api/tasks/tasks/
Authorization: Bearer <access_token>

# With filters
GET /api/tasks/tasks/?status=COMPLETED
GET /api/tasks/tasks/?start_date=2025-11-01&end_date=2025-11-05
GET /api/tasks/tasks/?search=title,description
GET /api/tasks/tasks/?ordering=-created_at,status,updated_at
Response:
json{
  "count": 25,
  "next": "http://localhost:8000/api/tasks/?page=2",
  "previous": null,
  "results": [
    {
      "id": 1,
      "title": "Process Customer Data",
      "status": "COMPLETED",
      "created_at": "2025-11-05T10:30:00Z",
      "updated_at": "2025-11-05T10:30:15Z"
    }
  ]
}
Get Single Task (with caching)
httpGET /api/tasks/1/
Authorization: Bearer <access_token>
Response:
json{
  "task": {
    "id": 1,
    "user": {
      "id": 1,
      "username": "john_doe",
      "email": "john@example.com"
    },
    "title": "Process Customer Data",
    "description": "Import and process customer CSV file",
    "status": "COMPLETED",
    "result": "Task completed successfully in 15 seconds at 2025-11-05T16:52:34.115391+00:00",  
    "celery_task_id": "8f7e2c3d-4b1a-5e6f-7g8h-9i0j1k2l3m4n",
    "created_at": "2025-11-05T10:30:00Z",
    "updated_at": "2025-11-05T10:30:15Z"
  },
  "cached": true
}

Delete Task

httpDELETE /api/tasks/tasks/1/
Authorization: Bearer <access_token>
Response:
json{
  "message": "Task 1 deleted successfully"
}

Task Statistics

httpGET /api/tasks/stats/
Authorization: Bearer <access_token>
Response:
json{
  "stats": [
    {"status": "PENDING", "count": 5},
    {"status": "PROCESSING", "count": 2},
    {"status": "COMPLETED", "count": 18},
    {"status": "FAILED", "count": 1}
  ],
  "total": 26
}
Admin - View All Tasks
httpGET /api/admin/tasks/
Authorization: Bearer <admin_access_token>

# With filters
GET /api/admin/tasks/?status=FAILED
Response:
json{
  "count": 150,
  "tasks": [
    {
      "id": 1,
      "user": {
        "id": 1,
        "username": "john_doe",
        "email": "john@example.com"
      },
      "title": "Process Customer Data",
      "status": "COMPLETED",
      "created_at": "2025-11-05T10:30:00Z",
      "updated_at": "2025-11-05T10:30:15Z"
    }
  ]
}


Task Status Flow

PENDING → PROCESSING → COMPLETED/FAILED

PENDING: Task created, waiting for processing
PROCESSING: Task is being executed by Celery worker
COMPLETED: Task finished successfully
FAILED: Task encountered an error

Caching Strategy

Task details are cached in Redis with 5-minute TTL
Cache is invalidated on:

Task status update
Task deletion
Task result modification


Cache key format: task_queue:task:{task_id}

Celery Tasks
Background Task Processing

Simulates 10-20 second processing time
Auto-retries on failure (max 3 times)

Periodic Tasks (Celery Beat)

cleanup_old_tasks: Runs daily at midnight

Deletes completed/failed tasks older than 30 days
Frees up database storage


Environment Variables
Create a .env file in the project root:
env# Django
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database
DB_NAME=task_queue_db
DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=localhost
DB_PORT=5432

# Redis
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0

# Celery
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0

Error Handling
The API uses standard HTTP status codes:

200 OK: Successful GET, PUT, PATCH, DELETE
201 Created: Successful POST
400 Bad Request: Invalid request data
401 Unauthorized: Missing or invalid authentication
403 Forbidden: Insufficient permissions
404 Not Found: Resource doesn't exist
500 Internal Server Error: Server error

Error response format:
json{
  "error": "Detailed error message",
  "field_errors": {
    "title": ["This field is required."]
  }
}