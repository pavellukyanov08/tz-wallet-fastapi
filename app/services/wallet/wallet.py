import logging
from uuid import uuid4, UUID

from fastapi import HTTPException

from app.deps import CurrentActiveUserDep, check_user_admin
from app.common.adapters import PostgresStorageAdapter
from app.common.schemas import MessageDTO
from app.schemas.wallet import WalletRead, WalletUpdate


class WalletService:
    def __init__(
        self,
        *,
        logger: logging.Logger,
        postgres_adapter: PostgresStorageAdapter,
    ) -> None:
        self._logger = logger
        self._postgres_adapter = postgres_adapter

    async def commit_wallet(self) -> None:
        await self._postgres_adapter.commit()

    async def get_user_wallet(
        self,
        *,
        current_user: CurrentActiveUserDep,
    ) -> WalletRead:
        wallet_sid = current_user.wallet.sid
        wallet = await self._postgres_adapter.get_wallet(wallet_sid=wallet_sid)
        if wallet is None:
            raise HTTPException(
                status_code=404,
                detail="Wallet not found"
            )
        return WalletRead.model_validate(wallet)

    async def get_wallet(
        self,
        *,
        current_user: CurrentActiveUserDep,
        wallet_sid: UUID,
    ) -> WalletRead | None:
        await check_user_admin(current_user=current_user)
        wallet = await self._postgres_adapter.get_wallet(wallet_sid=wallet_sid)
        if wallet is None:
            raise HTTPException(
                status_code=404,
                detail="Wallet not found"
            )
        return WalletRead.model_validate(wallet)

    async def update_wallet(
        self,
        *,
        current_user: CurrentActiveUserDep,
        data: WalletUpdate,
    ) -> MessageDTO:
        wallet_sid = current_user.wallet.sid
        wallet = await self._postgres_adapter.get_wallet(wallet_sid=wallet_sid)
        if wallet is None:
            raise HTTPException(
                status_code=404,
                detail="Wallet does not exist",
            )

        await self._postgres_adapter.update_wallet(
            data=data,
            wallet_sid=wallet_sid
        )
        await self._postgres_adapter.commit()
        return MessageDTO(message="Кошелёк обновлен")


