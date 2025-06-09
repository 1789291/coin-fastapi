from typing import Annotated
from fastapi import Depends, FastAPI
from fastapi.security import OAuth2PasswordRequestForm
from auth.schemas import Token
from database.session import SessionDep
from models import create_db_and_tables
from routers import auth, users,transactions, bank_accounts, listings, auctions

app = FastAPI(title="Users App")

# Include routers
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(transactions.router)
app.include_router(bank_accounts.router)
app.include_router(listings.router)
app.include_router(auctions.router)




@app.on_event("startup")
def on_startup():
    create_db_and_tables()

# Add this for compatibility
@app.post("/token", response_model=Token)  # In main.py
async def login_for_access_token_root(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()], 
    session: SessionDep
):
    """Root token endpoint for OAuth2 compatibility"""
    # Call the same logic as /auth/token
    return await auth.login_for_access_token(form_data, session)
