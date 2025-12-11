from datetime import datetime
from uuid import UUID, uuid4
from sqlalchemy import DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.enums import OperationTypeEnum
from app.utils import DateTimeManager


class Wallet(Base):
    __tablename__ = "wallet"

    sid: Mapped[UUID] = mapped_column(
        unique=True, primary_key=True, index=True, default=uuid4
    )
    total_amount: Mapped[float] = mapped_column()
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )
    user_sid: Mapped[UUID] = mapped_column(
        ForeignKey("user.sid", ondelete="CASCADE"),
    )

    user = relationship(
        "User",
        foreign_keys=[user_sid],
        back_populates="wallet",
    )

    operations = relationship(
        "Operation",
        back_populates="wallet",
        cascade="all, delete-orphan",
        lazy="selectin",
    )


class Operation(Base):
    __tablename__ = "operations"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    operation_type: Mapped[OperationTypeEnum] = mapped_column(
        comment="Operation type",
    )
    amount: Mapped[float] = mapped_column(
        default=0,
        comment="Operation type",
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now()
    )
    wallet_sid: Mapped[UUID] = mapped_column(
        ForeignKey("wallet.sid", ondelete="CASCADE"),
    )

    wallet = relationship(
        "Wallet",
        foreign_keys=[wallet_sid],
        back_populates="operations",
    )
