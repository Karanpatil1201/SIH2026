from typing import List, Optional
from datetime import datetime, timezone, timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.core.database import get_db
from app.models.database_models import UserDB, UserSessionDB, QueryHistoryDB, ActivityLogDB
from app.api.routers import get_current_user

router = APIRouter()

def get_current_admin(current_user: UserDB = Depends(get_current_user)) -> UserDB:
    if current_user.role.lower() != "admin" and current_user.username.lower() != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to access this resource"
        )
    return current_user

@router.get("/admin/dashboard")
def get_admin_dashboard(db: Session = Depends(get_db), current_admin: UserDB = Depends(get_current_admin)):
    total_users = db.query(UserDB).count()
    
    # Active users in last 24 hours
    one_day_ago = datetime.now(timezone.utc) - timedelta(days=1)
    active_users = db.query(UserSessionDB).filter(UserSessionDB.login_time >= one_day_ago).distinct(UserSessionDB.user_id).count()
    
    total_queries = db.query(QueryHistoryDB).count()
    
    today = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
    queries_today = db.query(QueryHistoryDB).filter(QueryHistoryDB.created_at >= today).count()
    
    total_sessions = db.query(UserSessionDB).count()
    
    recent_activity = db.query(ActivityLogDB).order_by(ActivityLogDB.created_at.desc()).limit(10).all()
    
    activities = []
    for log in recent_activity:
        user = db.query(UserDB).filter(UserDB.id == log.user_id).first()
        activities.append({
            "id": log.id,
            "user_id": log.user_id,
            "username": user.username if user else "Unknown",
            "action": log.action,
            "metadata": log.metadata_json,
            "created_at": log.created_at
        })
    
    return {
        "overview": {
            "total_users": total_users,
            "active_users": active_users,
            "total_queries": total_queries,
            "queries_today": queries_today,
            "total_sessions": total_sessions
        },
        "recent_activity": activities
    }

@router.get("/admin/users")
def get_admin_users(db: Session = Depends(get_db), current_admin: UserDB = Depends(get_current_admin)):
    users = db.query(UserDB).order_by(UserDB.created_at.desc()).all()
    
    result = []
    for user in users:
        queries_count = db.query(QueryHistoryDB).filter(QueryHistoryDB.user_id == user.id).count()
        result.append({
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "role": user.role,
            "is_active": user.is_active,
            "created_at": user.created_at,
            "last_login": user.last_login,
            "queries_count": queries_count
        })
        
    return result

@router.get("/admin/users/{user_id}")
def get_admin_user_detail(user_id: str, db: Session = Depends(get_db), current_admin: UserDB = Depends(get_current_admin)):
    user = db.query(UserDB).filter(UserDB.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
        
    sessions = db.query(UserSessionDB).filter(UserSessionDB.user_id == user_id).order_by(UserSessionDB.login_time.desc()).limit(10).all()
    queries_count = db.query(QueryHistoryDB).filter(QueryHistoryDB.user_id == user_id).count()
    
    return {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "role": user.role,
        "full_name": user.full_name,
        "phone_number": user.phone_number,
        "is_active": user.is_active,
        "created_at": user.created_at,
        "last_login": user.last_login,
        "queries_count": queries_count,
        "recent_sessions": [
            {
                "id": s.id,
                "login_time": s.login_time,
                "logout_time": s.logout_time
            } for s in sessions
        ]
    }

@router.get("/admin/users/{user_id}/queries")
def get_admin_user_queries(user_id: str, db: Session = Depends(get_db), current_admin: UserDB = Depends(get_current_admin)):
    queries = db.query(QueryHistoryDB).filter(QueryHistoryDB.user_id == user_id).order_by(QueryHistoryDB.created_at.desc()).limit(50).all()
    
    return [
        {
            "id": q.id,
            "query": q.query,
            "language": q.language,
            "latitude": q.latitude,
            "longitude": q.longitude,
            "response_status": q.response_status,
            "created_at": q.created_at
        } for q in queries
    ]

@router.get("/admin/activity")
def get_admin_activity(limit: int = 50, db: Session = Depends(get_db), current_admin: UserDB = Depends(get_current_admin)):
    activities = db.query(ActivityLogDB).order_by(ActivityLogDB.created_at.desc()).limit(limit).all()
    
    result = []
    for log in activities:
        user = db.query(UserDB).filter(UserDB.id == log.user_id).first()
        result.append({
            "id": log.id,
            "user_id": log.user_id,
            "username": user.username if user else "Unknown",
            "action": log.action,
            "metadata": log.metadata_json,
            "created_at": log.created_at
        })
        
    return result
