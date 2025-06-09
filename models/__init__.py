from sqlmodel import SQLModel, Relationship, Field, create_engine
from pydantic import EmailStr
from typing import Literal, Optional, List
from pydantic_extra_types.phone_numbers import PhoneNumber
from datetime import datetime
from enum import Enum


class UserRole(Enum):
    USER = "USER"
    ADMIN = "ADMIN"


class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(unique=True)
    name: str = Field(max_length=50)
    surname: str = Field(max_length=50)
    email: EmailStr
    cell: PhoneNumber
    password_hash: str
    coin_balance: Optional[float] = None
    role: UserRole = Field(default=UserRole.USER)

    # Relationships
    bank_account: Optional["BankAccount"] = Relationship(back_populates="owner")

    referrals_made: List["Referral"] = Relationship(
        back_populates="referrer",
        sa_relationship_kwargs={"foreign_keys": "[Referral.referrer_id]"},
    )
    referral_record: Optional["Referral"] = Relationship(
        back_populates="referred",
        sa_relationship_kwargs={"foreign_keys": "[Referral.referred_id]"},
    )

    # Fixed: Added listings relationship
    listings: List["Listing"] = Relationship(back_populates="seller")

    transactions_bought: List["Transaction"] = Relationship(
        back_populates="buyer",
        sa_relationship_kwargs={"foreign_keys": "[Transaction.buyer_id]"},
    )
    transactions_sold: List["Transaction"] = Relationship(
        back_populates="seller",
        sa_relationship_kwargs={"foreign_keys": "[Transaction.seller_id]"},
    )


class BankAccount(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(max_length=50)
    number: int = Field(ge=0, le=999999)
    branch_code: int = Field(ge=0, le=999999)

    user_id: Optional[int] = Field(default=None, foreign_key="user.id")
    owner: Optional[User] = Relationship(back_populates="bank_account")


class Referral(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    referrer_id: int = Field(foreign_key="user.id")
    referred_id: int = Field(foreign_key="user.id")
    date: datetime

    referrer: Optional["User"] = Relationship(
        back_populates="referrals_made",
        sa_relationship_kwargs={"foreign_keys": "[Referral.referrer_id]"},
    )
    referred: Optional["User"] = Relationship(
        back_populates="referral_record",
        sa_relationship_kwargs={"foreign_keys": "[Referral.referred_id]"},
    )


class AuctionStatus(Enum):
    UPCOMING = "UPCOMING"
    STARTED = "STARTED"
    ENDED = "ENDED"


class Auction(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    start_time: datetime
    end_time: datetime
    status: AuctionStatus = Field(default=AuctionStatus.UPCOMING)

    # Fixed: lowercase back_populates and List type
    listings: List["Listing"] = Relationship(back_populates="auction")


class Listing(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    amount: float
    seller_id: int = Field(foreign_key="user.id")
    date: datetime
    auction_id: int = Field(foreign_key="auction.id")

    # Relationships
    auction: Optional[Auction] = Relationship(back_populates="listings")
    # Fixed: should point to seller's listings, not transactions_sold
    seller: Optional[User] = Relationship(back_populates="listings")
    transaction: Optional["Transaction"] = Relationship(back_populates="listing")


class Transaction(SQLModel, table=True):  # Fixed: class name spelling
    id: Optional[int] = Field(default=None, primary_key=True)
    buyer_id: int = Field(foreign_key="user.id")
    seller_id: int = Field(foreign_key="user.id")
    status: str
    date: datetime
    listing_id: int = Field(
        foreign_key="listing.id", unique=True
    )  # Unique constraint for 1:1

    # Relationships
    listing: Optional[Listing] = Relationship(back_populates="transaction")
    buyer: Optional[User] = Relationship(
        back_populates="transactions_bought",
        sa_relationship_kwargs={"foreign_keys": "[Transaction.buyer_id]"},
    )
    seller: Optional[User] = Relationship(
        back_populates="transactions_sold",
        sa_relationship_kwargs={"foreign_keys": "[Transaction.seller_id]"},
    )


db_name = "auction.db"
db_url = f"sqlite:///{db_name}"
engine = create_engine(db_url, echo=True)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)
