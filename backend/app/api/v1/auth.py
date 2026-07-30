from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.database import get_db
from app.models.user import User
from app.schemas.schemas import UserLogin, Token, UserResponse
from app.core.security import verify_password, create_access_token, get_password_hash, RoleChecker

router = APIRouter()


@router.post("/login", response_model=Token)
async def login(credentials: UserLogin, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.username == credentials.username))
    user = result.scalars().first()
    
    # Auto-seed admin user if login attempted with admin/admin123 and no user exists
    if not user and credentials.username == "admin" and credentials.password == "admin123":
        user = User(
            username="admin",
            email="admin@agentguard.ai",
            hashed_password=get_password_hash("admin123"),
            full_name="Enterprise Admin",
            role="Admin"
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)

    if not user or not verify_password(credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(subject=user.username, role=user.role)
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "role": user.role,
        "username": user.username
    }


@router.get("/me", response_model=UserResponse)
async def get_current_user(
    token_payload: dict = Depends(RoleChecker(allowed_roles=["Admin", "Auditor", "Developer"])),
    db: AsyncSession = Depends(get_db)
):
    username = token_payload.get("sub")
    result = await db.execute(select(User).where(User.username == username))
    user = result.scalars().first()
    if not user:
        # Return synthetic auditor if fallback token
        return UserResponse(
            id=1,
            username=username or "auditor",
            email=f"{username or 'auditor'}@agentguard.ai",
            role=token_payload.get("role", "Auditor"),
            full_name="Enterprise Compliance Auditor"
        )
    return user
