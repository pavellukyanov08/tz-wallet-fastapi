from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, Field
from app.enums import OperationTypeEnum


class OperationBase(BaseModel):
    operation_type: OperationTypeEnum = Field(..., description="Type of operation")
    amount: float = Field(...)


class Operation(OperationBase):
    pass


class OperationCreate(Operation):
    wallet_sid: UUID = Field(..., description="SID of wallet")
    amount: float = Field(...)

