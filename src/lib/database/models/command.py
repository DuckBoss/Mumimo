from typing import TYPE_CHECKING, Any, Dict, List, Optional

from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from .. import metadata

if TYPE_CHECKING:
    from .permission_group import PermissionGroupTable
    from .plugin import PluginTable


class CommandTable(metadata.Base):
    __tablename__ = "command"

    id: Mapped[int] = mapped_column(primary_key=True, nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)

    # One to many to permission groups
    permission_groups: Mapped[List["PermissionGroupTable"]] = relationship(back_populates="command")

    # Nullable many-to-one to plugins
    plugin: Mapped[Optional["PluginTable"]] = relationship(back_populates="commands")
    plugin_id: Mapped[Optional[int]] = mapped_column(ForeignKey("plugin.id"))

    created_on: Mapped[DateTime] = mapped_column(DateTime(timezone=True), default=func.now(), server_default=func.now(), nullable=False)
    updated_on: Mapped[DateTime] = mapped_column(DateTime(timezone=True), default=func.now(), onupdate=func.now(), nullable=False)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "permission_groups": [group.to_dict() for group in self.permission_groups],
            "created_on": self.created_on,
            "updated_on": self.updated_on,
        }

    def __repr__(self) -> str:
        return (
            f"Command(id={self.id!r}, name={self.name!r}, permission_groups={self.permission_groups!r}, "
            f"created_on={self.created_on!r}, updated_on={self.updated_on!r})"
        )
