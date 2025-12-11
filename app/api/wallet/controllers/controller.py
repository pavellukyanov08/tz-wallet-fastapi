from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Body, Path

from app.settings import api_settings
from .deps import WalletServiceDep
from app.deps import CurrentActiveUserDep
from app.schemas.wallet import WalletRead, WalletUpdate
from app.common.schemas import MessageDTO


router = APIRouter(
    prefix=api_settings.WALLETS_PREFIX,
)


@router.get('/get_wallet', response_model=WalletRead)
async def get_user_wallet(
    service: WalletServiceDep,
    current_user: CurrentActiveUserDep,
) -> WalletRead:
    """
    Get current user wallet
    """
    return await service.get_user_wallet(current_user=current_user)


@router.get('/{walletSid}', response_model=WalletRead)
async def get_wallet(
    service: WalletServiceDep,
    current_user: CurrentActiveUserDep,
    wallet_sid: Annotated[UUID, Path(..., alias="walletSid")]
) -> WalletRead:
    """
    Get any wallet
    """
    return await service.get_wallet(wallet_sid=wallet_sid, current_user=current_user)


@router.put('/{walletSid}/operation', response_model=MessageDTO)
async def update_wallet(
    service: WalletServiceDep,
    current_user: CurrentActiveUserDep,
    data: Annotated[WalletUpdate, Body(...)],
) -> MessageDTO:

    await service.update_wallet(current_user=current_user, data=data)

    return MessageDTO(message="Кошелек обновлен")





