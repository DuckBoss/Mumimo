from typing import TYPE_CHECKING, Any, Dict, List

from sqlalchemy import DateTime, String, ForeignKey, Table, Column
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from .. import metadata

if TYPE_CHECKING:
    from .alias import AliasTable
    from .permission_group import PermissionGroupTable

user_permission_association_table = Table(
    "user_permission_association_table",
    metadata.Base.metadata,
    Column("user_id", ForeignKey("user.id")),
    Column("permission_group_id", ForeignKey("permission_group.id")),
)


class UserTable(metadata.Base):
    __tablename__ = "user"

    id: Mapped[int] = mapped_column(primary_key=True, nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)

    # One to many to permission groups
    permission_groups: Mapped[List["PermissionGroupTable"]] = relationship(secondary=user_permission_association_table)
    # One to many to aliases
    aliases: Mapped[List["AliasTable"]] = relationship()

    created_on: Mapped[DateTime] = mapped_column(DateTime(timezone=True), default=func.now(), server_default=func.now(), nullable=False)
    updated_on: Mapped[DateTime] = mapped_column(DateTime(timezone=True), default=func.now(), onupdate=func.now(), nullable=False)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "permission_groups": [group.to_dict() for group in self.permission_groups],
            "aliases": [alias.to_dict() for alias in self.aliases],
            "created_on": self.created_on,
            "updated_on": self.updated_on,
        }

    def __repr__(self) -> str:
        return (
            f"User(id={self.id!r}, name={self.name!r}, permission_groups={self.permission_groups!r}, "
            f"aliases={self.aliases!r}, created_on={self.created_on!r}, updated_on={self.updated_on!r})"
        )
