import logging
from uuid import UUID

from app.common.adapters import PostgresStorageAdapter

from app.common.schemas import MessageDTO
from app.deps import (
    validate_auth_user,
    create_access_token,
    create_refresh_token,
    CurrentUserRefreshDep,
    CurrentActiveUserDep
)
from app.enums import TokenTypeEnum
from app.schemas.user import AuthLogin
from app.schemas.token import TokenPair, RefreshToken


class AuthService:
    def __init__(
        self,
        *,
        logger: logging.Logger,
        postgres_adapter: PostgresStorageAdapter
    ) -> None:
        self._logger = logger
        self._postgres_adapter = postgres_adapter

    @staticmethod
    def refresh_token(
        *,
        current_user: CurrentUserRefreshDep
    ) -> RefreshToken:
        access_token = create_access_token(user_data=current_user)
        return RefreshToken(
            access_token=access_token,
            token_type=TokenTypeEnum.BEARER
        )

    async def login(
        self,
        *,
        user_data: AuthLogin
    ) -> TokenPair:
        await validate_auth_user(
            user_data=user_data,
            postgres=self._postgres_adapter
        )
        access_token = create_access_token(
            user_data=user_data
        )
        refresh_token = create_refresh_token(
            user_data=user_data
        )
        return TokenPair(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type=TokenTypeEnum.BEARER
        )

    async def logout(
        self, *, user_sid: UUID, data: CurrentActiveUserDep
    ) -> MessageDTO:
        user = await self._postgres_adapter.get_user(user_sid=user_sid)
        if user is None:
            raise ValueError("Пользователя не существует")

        return MessageDTO(message="OK")
