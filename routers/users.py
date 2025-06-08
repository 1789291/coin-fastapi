from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status

from models import User
from database.session import SessionDep
from services.user_service import UserService
from auth.dependencies import get_current_active_user, require_admin

router = APIRouter(prefix="/users", tags=["users"])

@router.post("/register", status_code=status.HTTP_201_CREATED)
def register_user(user: User, session: SessionDep) -> User:
    """Register a new user"""
    return UserService.create_user(session, user)

@router.get("/", status_code=status.HTTP_200_OK)
def get_all_users(
    session: SessionDep, 
    current_user: Annotated[User, Depends(get_current_active_user)]
) -> list[User]:
    """Get all users - requires authentication"""
    return UserService.get_all_users(session)

@router.get("/me", response_model=User)
async def read_users_me(
    current_user: Annotated[User, Depends(get_current_active_user)],
):
    """Get current user profile"""
    return current_user

@router.get("/{username}", status_code=status.HTTP_200_OK)
def get_user_by_username(
    username: str,
    session: SessionDep,
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> User:
    """Get user by username - requires authentication"""
    user = UserService.get_user_by_username(session, username)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Users can only view their own profile unless they're admin
    if current_user.username != username and (
        not hasattr(current_user, "role") or current_user.role != "admin"
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to view this user",
        )
    return user

# Admin-only endpoints
@router.post("/", status_code=status.HTTP_200_OK)
def add_user(
    user: User,
    session: SessionDep,
    current_admin: Annotated[User, Depends(require_admin)],
) -> User:
    """Create a new user - requires admin role"""
    return UserService.create_user(session, user)

@router.delete("/{username}", status_code=status.HTTP_200_OK)
def delete_user(
    username: str,
    session: SessionDep,
    current_admin: Annotated[User, Depends(require_admin)],
):
    """Delete a user - admin only"""
    if not UserService.delete_user(session, username):
        raise HTTPException(status_code=404, detail="User not found")
    return {"message": f"User {username} deleted successfully"}

@router.put("/{username}/role", status_code=status.HTTP_200_OK)
def update_user_role(
    username: str,
    new_role: str,
    session: SessionDep,
    current_admin: Annotated[User, Depends(require_admin)],
):
    """Update user role - admin only"""
    user = UserService.update_user_role(session, username, new_role)
    return {"message": f"User {username} role updated to {new_role}"}
