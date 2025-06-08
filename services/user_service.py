from typing import Optional, List
from sqlmodel import Session, select
from fastapi import HTTPException, status

from models import User
from auth.password import verify_password, get_password_hash


class UserService:
    @staticmethod
    def authenticate_user(
        session: Session, username: str, password: str
    ) -> Optional[User]:
        """Authenticate a user with username and password"""
        statement = select(User).where(User.username == username)
        user = session.exec(statement).first()

        if not user:
            return None
        if not verify_password(password, user.password_hash):
            return None
        return user

    @staticmethod
    def create_user(session: Session, user: User) -> User:
        """Create a new user with hashed password"""
        # Check if user already exists
        existing_user = UserService.get_user_by_username(session, user.username)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already registered",
            )

        # Hash the password before storing
        user.password_hash = get_password_hash(user.password_hash)

        session.add(user)
        session.commit()
        session.refresh(user)
        return user

    @staticmethod
    def get_user_by_username(session: Session, username: str) -> Optional[User]:
        """Get user by username"""
        statement = select(User).where(User.username == username)
        return session.exec(statement).first()

    @staticmethod
    def get_all_users(session: Session) -> List[User]:
        """Get all users"""
        statement = select(User)
        return session.exec(statement).all()

    @staticmethod
    def delete_user(session: Session, username: str) -> bool:
        """Delete a user by username"""
        user = UserService.get_user_by_username(session, username)
        if not user:
            return False

        session.delete(user)
        session.commit()
        return True

    @staticmethod
    def update_user_role(session: Session, username: str, new_role: str) -> User:
        """Update user role"""
        user = UserService.get_user_by_username(session, username)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        if not hasattr(user, "role"):
            raise HTTPException(
                status_code=400, detail="User model doesn't support roles"
            )

        user.role = new_role
        session.add(user)
        session.commit()
        session.refresh(user)
        return user
