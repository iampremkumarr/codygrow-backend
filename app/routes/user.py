from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db import get_db
from app.models.user import User
from app.models.profile import UserProfile
from app.models.plan import UserPlan, PlanType
from app.schemas.profile import UserProfileOut, UserPlanOut, UpdatePlanRequest
from app.services.auth import get_current_user

router = APIRouter(prefix="/user", tags=["User"])


@router.get("/profile", response_model=UserProfileOut)
def get_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get the authenticated user's profile."""
    profile = (
        db.query(UserProfile)
        .filter(UserProfile.user_id == current_user.id)
        .first()
    )
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    return profile


@router.get("/plan", response_model=UserPlanOut)
def get_plan(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get the authenticated user's active plan."""
    plan = (
        db.query(UserPlan)
        .filter(UserPlan.user_id == current_user.id, UserPlan.is_active == True)
        .first()
    )
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")
    return plan


@router.put("/plan", response_model=UserPlanOut)
def update_plan(
    payload: UpdatePlanRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update the authenticated user's plan type."""
    try:
        new_plan_type = PlanType(payload.plan_type)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid plan type. Use 'free' or 'studio'.")

    plan = (
        db.query(UserPlan)
        .filter(UserPlan.user_id == current_user.id, UserPlan.is_active == True)
        .first()
    )
    if not plan:
        raise HTTPException(status_code=404, detail="Active plan not found")

    plan.plan_type = new_plan_type
    db.commit()
    db.refresh(plan)
    return plan
