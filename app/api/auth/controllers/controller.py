from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm, HTTPBearer

from app.common.schemas import MessageDTO
from app.settings import api_settings
from .deps import AuthServiceDep
from app.deps import CurrentUserRefreshDep, CurrentActiveUserDep
from app.schemas.token import TokenPair, RefreshToken
from app.schemas.user import AuthLogin


http_bearer = HTTPBearer(auto_error=False)

router = APIRouter(
    prefix=api_settings.AUTH_USERS_PREFIX,
    dependencies=[Depends(http_bearer)],
)


@router.post('/login', response_model=TokenPair)
async def login(
    service: AuthServiceDep,
    data: AuthLogin
) -> TokenPair:

    return await service.login(user_data=data)


@router.post('/login_swagger', response_model=TokenPair)
async def login_swagger(
    service: AuthServiceDep,
    data: Annotated[OAuth2PasswordRequestForm, Depends()],
) -> TokenPair:
    auth_data = AuthLogin(
        email=data.username,
        password=data.password
    )

    return await service.login(user_data=auth_data)


@router.post('/refresh', response_model=RefreshToken)
async def refresh_token(
    service: AuthServiceDep,
    current_user: CurrentUserRefreshDep
) -> RefreshToken:

    return service.refresh_token(current_user=current_user)


# @router.post('/logout', response_model=MessageDTO)
# async def logout(
#     service: AuthServiceDep,
#     current_user: CurrentActiveUserDep
# ) -> MessageDTO:
#     await service.logout(user_data=current_user)
#
#     return MessageDTO(message="Успешный выход из системы")