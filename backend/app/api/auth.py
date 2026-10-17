
import jwt
from app.models import Member
from app.schemas.auth import MemberLinkRequest
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models import User
from app.schemas.auth import (
    UserCreate,
    UserResponse,
    Token,
    LoginRequest,
)
from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    decode_access_token,
)


router = APIRouter(prefix="/auth", tags=["Authentication"])
bearer_scheme = HTTPBearer(auto_error=False)


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(
        bearer_scheme
    ),
    db: Session = Depends(get_db),
) -> User:
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        payload = decode_access_token(credentials.credentials)
        user_id = int(payload["sub"])
    except (jwt.InvalidTokenError, ValueError, TypeError, KeyError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired access token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = db.get(User, user_id)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is inactive",
        )

    return user


@router.post(
    "/signup",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
def signup(
    data: UserCreate,
    db: Session = Depends(get_db),
):
    email = str(data.email).strip().lower()

    existing_user = (
        db.query(User)
        .filter(User.email == email)
        .first()
    )

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An account with this email already exists",
        )

    user = User(
        name=data.name.strip(),
        email=email,
        hashed_password=hash_password(data.password),
        role="member",
        is_active=True,
    )

    db.add(user)

    try:
        db.commit()
        db.refresh(user)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An account with this email already exists",
        )

    return user

@router.post("/login", response_model=Token)
def login(
    data: LoginRequest,
    db: Session = Depends(get_db),
):
    identifier = (data.phone or data.email or "").strip()

    if not identifier:
        raise HTTPException(
            status_code=422,
            detail="Phone number or email is required",
        )

    if "@" in identifier:
        user = (
            db.query(User)
            .filter(User.email == identifier.lower())
            .first()
        )
    else:
        member = (
            db.query(Member)
            .filter(Member.phone == identifier)
            .first()
        )

        user = None
        if member is not None:
            user = (
                db.query(User)
                .filter(User.member_id == member.id)
                .first()
            )

    if user is None or not verify_password(
        data.password,
        user.hashed_password,
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid phone/email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is inactive",
        )

    return {
        "access_token": create_access_token(user.id),
        "token_type": "bearer",
    }



@router.get("/me", response_model=UserResponse)
def get_me(
    current_user: User = Depends(get_current_user),
):
    return current_user

def require_admin(
    current_user: User = Depends(get_current_user),
) -> User:
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required",
        )

    return current_user



@router.post(
    "/users/{user_id}/link-member",
    response_model=UserResponse,
)
def link_member_account(
    user_id: int,
    data: MemberLinkRequest,
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    user = db.get(User, user_id)

    if user is None:
        raise HTTPException(
            status_code=404,
            detail="User not found",
        )

    if user.role != "member":
        raise HTTPException(
            status_code=400,
            detail="Only member accounts can be linked",
        )

    if user.member_id is not None:
        raise HTTPException(
            status_code=409,
            detail="This account is already linked",
        )

    member = db.get(Member, data.member_id)

    if member is None:
        raise HTTPException(
            status_code=404,
            detail="Gym member profile not found",
        )

    existing_link = (
        db.query(User)
        .filter(User.member_id == data.member_id)
        .first()
    )

    if existing_link:
        raise HTTPException(
            status_code=409,
            detail="This gym member is already linked to an account",
        )

    user.member_id = member.id

    try:
        db.commit()
        db.refresh(user)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="Could not link this member account",
        )

    return user