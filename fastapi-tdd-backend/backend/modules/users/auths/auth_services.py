import uuid
from datetime import datetime, timedelta, timezone
from xml.dom import ValidationErr

import bcrypt
import jwt
from databases import Database
from icecream import ic
from loguru import logger
from modules.users.auths.auth_exceptions import AuthExceptions
from modules.users.auths.auth_repositories import AuthRepository
from modules.users.auths.auth_schemas import (
    AccessToken,
    AuthEmailRecoverPsw,
    AuthResetPsw,
    AuthResponse,
    JWTCreds,
    JWTMeta,
    JWTPayload,
)
from modules.users.users.user_schemas import UserInDB, UserPasswordUpdate
from passlib.context import CryptContext
from pydantic import ValidationError
from shared.core.config import (
    ACCESS_TOKEN_EXPIRE_MINUTES,
    JWT_ALGORITHM,
    JWT_AUDIENCE,
    SECRET_KEY,
)
from shared.utils.service_result import ServiceResult

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class AuthService:
    def create_salt_and_hashedpassword(self, plaintext_password: str) -> str:
        salt = self._generate_salt()
        hashed_password = self._hash_password(password=plaintext_password, salt=salt)

        return UserPasswordUpdate(salt=salt, password=hashed_password)

    def _generate_salt(self) -> str:
        return bcrypt.gensalt().decode()

    def _hash_password(self, *, password: str, salt: str) -> str:
        return pwd_context.hash(password + salt)

    def verify_password(self, password: str, salt: str, hashed_pw: str) -> bool:
        return pwd_context.verify(password + salt, hashed_pw)

    def create_access_token_for_user(
        self,
        *,
        user: UserInDB,
        secret_key: str = str(SECRET_KEY),
        audience: str = JWT_AUDIENCE,
        expires_in: int = ACCESS_TOKEN_EXPIRE_MINUTES,
    ) -> str:
        if not user or not isinstance(user, UserInDB):
            return None

        creation_time = datetime.now().replace(tzinfo=None)
        expire_time = creation_time + timedelta(minutes=expires_in)

        jwt_meta = JWTMeta(
            aud=audience,
            iat=datetime.timestamp(creation_time),
            exp=datetime.timestamp(expire_time),
        )

        jwt_creds = JWTCreds(sub=user.email, username=user.username)
        token_payload = JWTPayload(
            **jwt_meta.dict(),
            **jwt_creds.dict(),
        )
        access_token = jwt.encode(token_payload.dict(), secret_key, algorithm=JWT_ALGORITHM)

        return access_token

    async def authenticate_user(self, username: str, password: str, db: Database) -> ServiceResult:
        from shared.utils.crypto_credentials import CryptoAES

        if not username:
            logger.error("Try to login without username")
            return ServiceResult(AuthExceptions.AuthNoUsernameException())

        if not password:
            logger.error("Try to login without password")
            return ServiceResult(AuthExceptions.AuthNoPasswordException())

        user = await AuthRepository(db).authenticate_user(username=username, password=password)

        if not user:
            logger.error(f"Trying to login with invalid credentials, username: {username}")
            return ServiceResult(AuthExceptions.AuthNoValidCredencialsException())

        if not self.verify_password(password=password, salt=user.salt, hashed_pw=user.password):
            logger.error(f"Trying to login with invalid credentials, username: {username}")
            return ServiceResult(AuthExceptions.AuthNoValidCredencialsException())

        user_autenticated = AuthResponse(
            access_token=self.create_access_token_for_user(user=user),
            token_type="bearer",
            id=user.id,
            fullname=user.fullname,
            username=user.username,
            role=user.role,
            permissions=user.permissions,
        )

        return ServiceResult(user_autenticated)

    def get_username_from_token(self, token: str, secret_key: str) -> str | None:
        try:
            decoded_token = jwt.decode(
                token,
                str(secret_key),
                audience=JWT_AUDIENCE,
                algorithms=[JWT_ALGORITHM],
            )
            payload = JWTPayload(**decoded_token)

        except (jwt.PyJWTError, ValidationError):
            raise AuthExceptions.AuthNoValidTokenCredentialsException()

        except jwt.ExpiredSignatureError:
            raise AuthExceptions.AuthTokenExpiredException()

        return payload.username


    async def verify_token(self, token: str, db: Database) -> ServiceResult:
        token_dict = await AuthRepository(db).get_token_by_value(token=token)

        if token_dict.get("token"):
            return ServiceResult(AuthExceptions.AuthRestPswTokenUsedException())

        return ServiceResult("token válido")

    async def reset_password(
        self, token: str, new_psw: AuthResetPsw, db: Database
    ) -> ServiceResult:
        from modules.users.users.user_repositories import UserRepository
        from modules.users.users.user_services import UserService
        from shared.utils.crypto_credentials import CryptoAES

        try:
            token_dict = await AuthRepository(db).get_token_by_value(token=token)

            if token_dict.get("token"):
                return ServiceResult(AuthExceptions.AuthRestPswTokenUsedException())

            secret_key: str = str(SECRET_KEY)
            decoded = jwt.decode(
                token, secret_key, audience=JWT_AUDIENCE, verify=True, algorithms=[JWT_ALGORITHM]
            )
            password = CryptoAES.decrypt(new_psw.new_psw)

            username = str(decoded.get("username"))
            user = await UserRepository(db).get_user_by_username(username=username)

            user_saved = await UserService(db).change_password_by_id(
                user.id, password, current_user=user
            )

            token_saved = await AuthRepository(db).save_token_used(token=token)

            result = ServiceResult("password cambiado con éxito")

        except jwt.exceptions.ExpiredSignatureError:
            result = ServiceResult(AuthExceptions.AuthRestPswTokenExpiredException())

        return result
