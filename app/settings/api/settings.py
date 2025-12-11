from pydantic_settings import BaseSettings


class ApiSettings(BaseSettings):
    AUTH_USERS_PREFIX: str = '/auth'
    USERS_PREFIX: str = '/users'
    WALLETS_PREFIX: str = '/wallets'


api_settings = ApiSettings()