from typing import Annotated
from fastapi import Depends
from app.services.wallet import WalletService
from app.common.deps import CommonPostgresDep
from app.utils import LoggerDep


def _get_wallet_service(
    logger: LoggerDep,
    postgres_adapter: CommonPostgresDep,
) -> WalletService:
    return WalletService(
        logger=logger,
        postgres_adapter=postgres_adapter,
    )


WalletServiceDep = Annotated[WalletService, Depends(_get_wallet_service)]
