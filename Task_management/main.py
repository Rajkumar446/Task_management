from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer
from database import engine, Base
from routers import user_routes, project_routes, task_routes
from apscheduler.schedulers.background import BackgroundScheduler
from utils.task_status_updater import update_task_status_daily
from utils.smart_email_notifications import (
    check_and_send_due_date_reminders,
    send_weekly_summary_to_team_leads
)

Base.metadata.create_all(bind=engine)

# Configure FastAPI with proper security documentation
app = FastAPI(
    title="Task Management API",
    
)

# Define security scheme for OpenAPI docs
from fastapi.openapi.utils import get_openapi
from fastapi.openapi.models import OAuthFlows as OAuthFlowsModel
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )
    openapi_schema["components"]["securitySchemes"] = {
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
        }
    }
    
    # Add security to all protected routes
    for path_data in openapi_schema["paths"].values():
        for operation in path_data.values():
            if isinstance(operation, dict) and "tags" in operation:
                # Skip login and register endpoints
                if operation.get("operationId") not in ["login_user_users_login_post", "register_user_users_register_post", "read_root__get"]:
                    operation["security"] = [{"BearerAuth": []}]
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi

@app.get("/")
def read_root():
    return {"message": "Task Management API is running!"}

@app.get("/health")
def health_check():
    """Health check endpoint for Docker container monitoring"""
    from datetime import datetime
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "Task Management API"
    }

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(user_routes.router)
app.include_router(project_routes.router)
app.include_router(task_routes.router)

# Setup scheduler for automated emails
scheduler = BackgroundScheduler()

# Daily task status updates
scheduler.add_job(update_task_status_daily, 'interval', days=1, next_run_time=None)

# 📧 SMART EMAIL SCHEDULES:
# Check due dates and overdue tasks daily at 9 AM
scheduler.add_job(
    check_and_send_due_date_reminders, 
    'cron', 
    hour=9, 
    minute=0,
    id='daily_due_date_check'
)

# Send weekly summary to team leads every Monday at 8 AM
scheduler.add_job(
    send_weekly_summary_to_team_leads,
    'cron',
    day_of_week='mon',
    hour=8,
    minute=0,
    id='weekly_team_summary'
)

scheduler.start()

# Shut down scheduler when exiting
import atexit
atexit.register(lambda: scheduler.shutdown())
