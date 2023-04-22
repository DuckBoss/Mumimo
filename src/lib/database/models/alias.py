from typing import TYPE_CHECKING, Any, Dict, List, Optional

from sqlalchemy import DateTime, ForeignKey, String, Table, Column, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from .. import metadata

if TYPE_CHECKING:
    from .permission_group import PermissionGroupTable


alias_permission_association_table = Table(
    "alias_permission_association_table",
    metadata.Base.metadata,
    Column("alias_id", ForeignKey("alias.id")),
    Column("permission_group_id", ForeignKey("permission_group.id")),
)


class AliasTable(metadata.Base):
    __tablename__ = "alias"

    id: Mapped[int] = mapped_column(primary_key=True, nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    command: Mapped[str] = mapped_column(String(1024), nullable=False)
    is_generic: Mapped[bool] = mapped_column(Boolean(), nullable=False, default=False)

    # One to many to permission groups
    permission_groups: Mapped[List["PermissionGroupTable"]] = relationship(secondary=alias_permission_association_table)

    # One to many nullable user
    user_id: Mapped[Optional[int]] = mapped_column(ForeignKey("user.id"))

    created_on: Mapped[DateTime] = mapped_column(DateTime(timezone=True), default=func.now(), server_default=func.now(), nullable=False)
    updated_on: Mapped[DateTime] = mapped_column(DateTime(timezone=True), default=func.now(), onupdate=func.now(), nullable=False)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "command": self.command,
            "is_generic": self.is_generic,
            "permission_groups": [group.to_dict() for group in self.permission_groups],
            "created_on": self.created_on,
            "updated_on": self.updated_on,
        }

    def __repr__(self) -> str:
        return (
            f"Alias(id={self.id!r}, name={self.name!r}, command={self.command!r}, is_generic={self.is_generic!r}, "
            f"permission_groups={self.permission_groups!r}, created_on={self.created_on!r}, updated_on={self.updated_on!r})"
        )
