from typing import TYPE_CHECKING, Any, Dict, List

from sqlalchemy import DateTime, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from .. import metadata

if TYPE_CHECKING:
    from .command import CommandTable


class PluginTable(metadata.Base):
    __tablename__ = "plugin"

    id: Mapped[int] = mapped_column(primary_key=True, nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)

    # One to many to commands
    commands: Mapped[List["CommandTable"]] = relationship(cascade="all, delete")

    created_on: Mapped[DateTime] = mapped_column(DateTime(timezone=True), default=func.now(), server_default=func.now(), nullable=False)
    updated_on: Mapped[DateTime] = mapped_column(DateTime(timezone=True), default=func.now(), onupdate=func.now(), nullable=False)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "commands": [command.to_dict() for command in self.commands],
            "created_on": self.created_on,
            "updated_on": self.updated_on,
        }

    def __repr__(self) -> str:
        return (
            f"Plugin(id={self.id!r}, name={self.name!r}, commands={self.commands!r}, "
            f"created_on={self.created_on!r}, updated_on={self.updated_on!r})"
        )
