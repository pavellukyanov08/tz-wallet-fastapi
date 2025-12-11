from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, Field
from app.schemas.operation import Operation
from app.enums import OperationTypeEnum


class Wallet(BaseModel):
    operations: list[Operation] = Field(...)
    total_amount: float = Field(...)


class WalletBase(Wallet):
    pass


class WalletOperation(BaseModel):
    amount: float = Field(...)
    operation_type: OperationTypeEnum = Field(...)


class WalletCreate(BaseModel):
    sid: UUID = Field(..., description="SID of wallet")
    total_amount: float = Field(default=0)


class WalletUpdate(WalletOperation):
    updated_at: datetime = Field(..., description="Wallet updated at")


class WalletRead(WalletBase):
    sid: UUID = Field(..., description="SID of wallet")
    user_sid: UUID = Field(..., description="SID of user")
    created_at: datetime = Field(..., description="Wallet created at")
    updated_at: datetime = Field(..., description="Wallet updated at")


