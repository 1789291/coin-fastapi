from sqlmodel import SQLModel, Field, create_engine
from pydantic import EmailStr
from typing import Optional


class User(SQLModel, table=True):
    id: int | None = Field(primary_key=True)
    username: str = Field(unique=True)
    name: str = Field(max_length=50)
    surname: str = Field(max_length=50)
    email: EmailStr
    password_hash: str
    role: Optional[str] = Field(default="user")


db_name = "users.db"
db_url = f"sqlite:///{db_name}"
engine = create_engine(db_url, echo=True)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)
