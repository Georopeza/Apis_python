from databases import Database
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from modules.users.auths.auth_services import AuthService
from modules.users.auths.auth_exceptions import AuthExceptions
from modules.users.users.user_repositories import UserRepository
from modules.users.users.user_schemas import UserInDB
from shared.core.config import SECRET_KEY, API_PREFIX
from shared.core.db.db_dependencies import get_database


oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{API_PREFIX}/users/login/")


async def get_user_from_token(
    *, token: str = Depends(oauth2_scheme), db: Database = Depends(get_database)
) -> UserInDB | None:
    user_repo = UserRepository(db)
    user = None
    try:
        username = AuthService().get_username_from_token(
            token=token, secret_key=str(SECRET_KEY)
        )
        user = await user_repo.get_user_by_username(username=username)
    except Exception as e:
        raise e

    return user


def get_current_active_user(
    current_user: UserInDB = Depends(get_user_from_token),
) -> UserInDB | None:
    if not current_user:
        raise AuthExceptions.AuthUnauthorizedException()
    if not current_user.is_active:
        raise AuthExceptions.AuthUnauthorizedException()
    return current_user
