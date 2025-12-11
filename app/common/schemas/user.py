from datetime import datetime
from uuid import UUID
from pydantic import Field
from .base import EmailDTO

from app.enums import UserRoleEnum
from app.utils.normalize_datetime import NormalizeDateTime
from app.schemas.wallet import WalletCreate, WalletRead


class UserDTO(NormalizeDateTime, EmailDTO):
    sid: UUID = Field(..., description="SID of user")
    fullname: str = Field(..., description="First, middle, last of user")
    role: UserRoleEnum = Field(default=UserRoleEnum.USER, description="Role of user")
    is_active: bool = Field(default=True, description="Status of user")
    wallet: WalletCreate = Field(default_factory=WalletCreate, description="Wallet of user")
    hashed_password: str = Field(..., description="Password of user")
    created_at: datetime = Field(..., description="User created at")
    updated_at: datetime = Field(..., description="User updated at")
