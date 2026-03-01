from fastapi import Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.clients.database_clients import get_db
from app.core.security import verify_token
from app.core.exceptions import UnauthorizedException
from app.models.user_model import User
from app.repositories.user_repository import UserRepository

security = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
) -> User:
    token = credentials.credentials
    user_id = verify_token(token)
    if user_id is None:
        raise UnauthorizedException("Could not validate credentials")

    # Use repository layer instead of raw db.query
    user = UserRepository(db).get_by_id(user_id)
    if user is None:
        raise UnauthorizedException("Could not validate credentials")

    return user


def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    return current_user