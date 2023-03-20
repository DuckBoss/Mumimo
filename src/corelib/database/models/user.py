from typing import TYPE_CHECKING, Any, Dict

from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from .. import metadata

if TYPE_CHECKING:
    from .permission_group import PermissionGroupTable


class UserTable(metadata.Base):
    __tablename__ = "user"

    id: Mapped[int] = mapped_column(primary_key=True, nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    permission_group_id: Mapped[int] = mapped_column(ForeignKey("permission_group.id"))

    permission_groups: Mapped["PermissionGroupTable"] = relationship(back_populates="users")
    created_on: Mapped[DateTime] = mapped_column(DateTime(timezone=True), default=func.now(), server_default=func.now(), nullable=False)
    updated_on: Mapped[DateTime] = mapped_column(DateTime(timezone=True), default=func.now(), onupdate=func.now(), nullable=False)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "permission_group_id": self.permission_group_id,
            "created_on": self.created_on,
            "updated_on": self.updated_on,
        }

    def __repr__(self) -> str:
        return f"User(id={self.id!r}, name={self.name!r}, permission_group_id={self.permission_group_id!r})"
