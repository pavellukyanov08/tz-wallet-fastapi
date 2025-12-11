import logging
from typing import cast
from uuid import UUID

from fastapi import HTTPException
from pydantic import EmailStr
from sqlalchemy import ColumnElement, select, update
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.enums import OperationTypeEnum
from app.models.user import User
from app.models.wallet import Wallet, Operation
from app.common.schemas import UserDTO
from app.schemas.wallet import WalletRead, WalletUpdate
from app.utils import DateTimeManager


class PostgresStorageAdapter:
    def __init__(
        self,
        *,
        logger: logging.Logger,
        postgres_session: AsyncSession,

    ) -> None:
        self._logger = logger
        self._postgres_session = postgres_session

    async def commit(self) -> None:
        try:
            await self._postgres_session.commit()
            self._logger.info("Changes has been commited")
        except Exception as e:
            self._logger.error("Error while commiting changes: %s", e)
            await self.rollback()
            raise

    async def rollback(self) -> None:
        try:
            await self._postgres_session.rollback()
            self._logger.info("Changes has been cancelled")
        except Exception as e:
            self._logger.error("Error when cancelling changes: %s", e)
            raise

    @staticmethod
    def _create_user_model(
        *,
        user_alchemy_model: User,
    ) -> UserDTO:
        return UserDTO(
            sid=user_alchemy_model.sid,
            email=cast(EmailStr, user_alchemy_model.email),
            fullname=user_alchemy_model.fullname,
            role=user_alchemy_model.role,
            wallet=user_alchemy_model.wallet,
            hashed_password=user_alchemy_model.hashed_password,
            created_at=user_alchemy_model.created_at,
            updated_at=user_alchemy_model.created_at,
        )

    async def _get_user_model(
        self,
        *,
        user_result: ColumnElement[bool]
    ) -> UserDTO | None:
        query = (
            select(User)
            .options(selectinload(User.wallet))
            .where(user_result)
        )
        stmt = await self._postgres_session.execute(query)
        result = stmt.scalar_one_or_none()

        if result is None:
            return None

        user_dto_model = UserDTO.model_validate(
            obj=result, from_attributes=True
        )
        return user_dto_model

    async def get_user(
        self,
        *,
        user_sid: UUID
    ) -> UserDTO | None:
        try:
            user_model = await self._get_user_model(
                user_result=(User.sid == user_sid),
            )

            self._logger.info(
                "Received user user_sid=%s",
                user_sid,
            )
            return user_model
        except Exception as e:
            self._logger.info(
                "Failed receiving user: user_sid=%s error=%s",
                user_sid,
                e,
            )
            raise

    async def get_user_by_email(
        self, *, user_email: EmailStr
    ) -> UserDTO | None:
        try:
            user_model = await self._get_user_model(
                user_result=(
                    User.email == user_email
                ),
            )
            self._logger.info(
                "Received user by user_email=%s",
                user_email,
            )
            return user_model
        except Exception as e:
            self._logger.info(
                "Failed to receive user: user_email=%s error=%s",
                user_email,
                e,
            )
            raise

    async def get_wallet(
        self,
        *,
        wallet_sid: UUID
    ) -> WalletRead:
        try:
            stmt = select(Wallet).where(Wallet.sid == wallet_sid)
            result = await self._postgres_session.execute(stmt)
            wallet: Wallet = result.scalar_one_or_none()
            self._logger.info(
                "Received wallet wallet_sid=%s",
                wallet_sid,
            )
            return WalletRead.model_validate(wallet, from_attributes=True)
        except Exception as e:
            self._logger.info(
                "Failed receiving wallet: wallet_sid=%s error=%s",
                wallet_sid,
                e,
            )
            raise

    async def update_wallet(
        self,
        *,
        data: WalletUpdate,
        wallet_sid: UUID,
    ) -> None:
        try:
            query = None
            if data.operation_type == OperationTypeEnum.WITHDRAW:
                query = (
                    update(Wallet)
                    .where(
                        Wallet.sid == wallet_sid,
                        Wallet.total_amount >= data.amount
                    )
                    .values(
                        total_amount=Wallet.total_amount - data.amount,
                        updated_at=data.updated_at,
                    )
                )
            elif data.operation_type == OperationTypeEnum.DEPOSIT:
                query = (
                    update(Wallet)
                    .where(
                        Wallet.sid == wallet_sid
                    )
                    .values(
                        total_amount=Wallet.total_amount + data.amount,
                        updated_at=data.updated_at,
                    )
                )

            if query is None:
                raise ValueError(f"Error while updating wallet")

            result = await self._postgres_session.execute(query)

            if data.operation_type == OperationTypeEnum.WITHDRAW and result.rowcount == 0:
                raise HTTPException(
                    status_code=400,
                    detail="Not enough funds for withdraw",
                )

            operation = Operation(
                operation_type=data.operation_type,
                amount=data.amount,
                wallet_sid=wallet_sid,
                created_at=DateTimeManager.get_now_utc(),
            )
            self._postgres_session.add(operation)
            self._logger.info("Wallet has been updated: %s",
                            wallet_sid
            )
        except SQLAlchemyError as e:
            self._logger.info("Error while updating wallet: %s", e)
            await self.rollback()
            raise

    async def check_user_exists(
        self,
        *,
        user_sid: UUID
    ) -> bool:
        query = select(User.sid).where(User.sid == user_sid)
        stmt = await self._postgres_session.execute(query)
        result = stmt.first()
        if result is None:
            return False
        return True

    async def create_user(self, *, user_model: UserDTO) -> None:
        try:
            if not await self.check_user_exists(user_sid=user_model.sid):
                user = User(
                    sid=user_model.sid,
                    fullname=user_model.fullname,
                    email=str(user_model.email),
                    role=user_model.role,
                    hashed_password=user_model.hashed_password,
                    created_at=user_model.created_at,
                    updated_at=user_model.created_at,
                )
                self._postgres_session.add(instance=user)
                await self._postgres_session.flush()

                wallet = Wallet(
                    sid=user_model.wallet.sid,
                    user_sid=user.sid,
                    total_amount=user_model.wallet.total_amount,
                    created_at=DateTimeManager.get_now_utc(),
                )
                self._postgres_session.add(wallet)

                self._logger.info("User has been created: %s", user_model.sid)
        except Exception as e:
            self._logger.error(
                "Failed creating user: sid=%s error=%s",
                user_model.sid,
                e,
            )
            await self.rollback()
            raise

    async def block_user(
        self,
        *,
        user_sid: UUID
    ) -> None:
        try:
            await self._postgres_session.execute(
                update(User)
                .where(User.sid == user_sid)
                .values(
                    is_active=False,
                    updated_at=DateTimeManager.get_now_utc(),
                )
            )
            self._logger.info(
                "Blocked user: sid=%s",
                user_sid,
            )
        except SQLAlchemyError as e:
            self._logger.error(
                "Failed to block user:sid=%s error=%s",
                user_sid,
                e,
            )
            await self.rollback()
            raise

    async def unlock_user(
        self,
        *,
        user_sid: UUID
    ) -> None:
        try:
            await self._postgres_session.execute(
                update(User)
                .where(User.sid == user_sid)
                .values(
                    is_active=True,
                    updated_at=DateTimeManager.get_now_utc(),
                )
            )
            self._logger.info(
                "Unlocked user: sid=%s",
                user_sid,
            )
        except SQLAlchemyError as e:
            self._logger.error(
                "Failed to unlock user:sid=%s error=%s",
                user_sid,
                e,
            )
            await self.rollback()
            raise