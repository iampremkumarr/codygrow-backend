from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.db import get_db
from app.models.user import User
from app.models.profile import UserProfile
from app.models.plan import UserPlan, PlanType
from app.schemas.auth import UserSignUp, Token, UserOut
from app.services.auth import hash_password, verify_password, create_access_token

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/signup", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def signup(payload: UserSignUp, db: Session = Depends(get_db)):
    """Register a new user and auto-create a profile + free plan."""
    existing = db.query(User).filter(User.email == payload.email).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    user = User(
        email=payload.email,
        hashed_password=hash_password(payload.password),
    )
    db.add(user)
    db.flush()  # Get the user.id without committing yet

    # Create profile (mirrors Supabase handle_new_user trigger)
    profile = UserProfile(user_id=user.id, full_name=payload.full_name)
    db.add(profile)

    # Create default free plan
    plan = UserPlan(user_id=user.id, plan_type=PlanType.free, is_active=True)
    db.add(plan)

    db.commit()
    db.refresh(user)

    # Attach full_name to response
    user.full_name = payload.full_name  # type: ignore
    return user


@router.post("/login", response_model=Token)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    """Login with email + password; returns a JWT access token."""
    user = db.query(User).filter(User.email == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = create_access_token(
        data={"sub": str(user.id), "email": user.email}
    )
    return {"access_token": token, "token_type": "bearer"}


@router.get("/me", response_model=UserOut)
def me(db: Session = Depends(get_db), token: str = ""):
    """Get current authenticated user (lightweight check)."""
    from app.services.auth import get_current_user, oauth2_scheme
    # This route is mainly a convenience; use /user/profile for full profile
    raise HTTPException(status_code=404, detail="Use /api/user/profile instead")
