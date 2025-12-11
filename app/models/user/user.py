from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import String, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.enums import UserRoleEnum

from app.utils import DateTimeManager


class User(Base):
    __tablename__ = "user"

    sid: Mapped[UUID] = mapped_column(
        unique=True, primary_key=True, index=True, default=uuid4
    )
    email: Mapped[str] = mapped_column(String(length=100), index=True, unique=True, comment="Email of user")
    fullname: Mapped[str] = mapped_column(index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(
        comment="Hashed password of user"
    )
    role: Mapped[UserRoleEnum] = mapped_column(
        default=UserRoleEnum.USER,
        comment="Role of user",
        server_default=UserRoleEnum.USER.value
    )
    is_active: Mapped[bool] = mapped_column(default=True, nullable=False, comment="User status")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )

    wallet = relationship(
        "Wallet",
        back_populates="user",
        cascade="all, delete-orphan",
        single_parent=True,
        lazy="selectin",
        uselist=False
    )
