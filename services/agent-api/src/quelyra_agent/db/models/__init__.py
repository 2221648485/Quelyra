from __future__ import annotations

import enum
import uuid
from datetime import UTC, datetime
from typing import Any

from sqlalchemy import JSON, Boolean, DateTime, Enum, ForeignKey, Index, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


def utcnow() -> datetime:
    """返回带 UTC 时区的当前时间。"""
    return datetime.now(UTC)


class Base(DeclarativeBase):
    pass


class UUIDTimestampMixin:
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)


class WorkspaceRole(str, enum.Enum):
    owner = "owner"
    admin = "admin"
    analyst = "analyst"


class User(UUIDTimestampMixin, Base):
    __tablename__ = "users"
    email: Mapped[str] = mapped_column(String(320), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(200))
    password_hash: Mapped[str] = mapped_column(String(500))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)


class Workspace(UUIDTimestampMixin, Base):
    __tablename__ = "workspaces"
    name: Mapped[str] = mapped_column(String(200))


class WorkspaceMember(Base):
    __tablename__ = "workspace_members"
    __table_args__ = (Index("ix_workspace_members_user", "user_id"),)
    workspace_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("workspaces.id", ondelete="CASCADE"), primary_key=True)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    role: Mapped[WorkspaceRole] = mapped_column(Enum(WorkspaceRole, native_enum=False, length=16))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)


class AuthSession(UUIDTimestampMixin, Base):
    __tablename__ = "auth_sessions"
    __table_args__ = (Index("ix_auth_sessions_user_active", "user_id", "revoked_at"),)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    family_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("auth_session_families.id", ondelete="CASCADE"), index=True
    )
    refresh_token_hash: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    rotated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    revoked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class AuthSessionFamily(UUIDTimestampMixin, Base):
    __tablename__ = "auth_session_families"
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    revoked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class WorkspaceResourceMixin(UUIDTimestampMixin):
    workspace_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("workspaces.id", ondelete="CASCADE"), index=True)


class DataSource(WorkspaceResourceMixin, Base):
    __tablename__ = "datasources"
    __table_args__ = (UniqueConstraint("workspace_id", "name", name="uq_datasources_workspace_name"),)
    name: Mapped[str] = mapped_column(String(200))
    engine: Mapped[str] = mapped_column(String(32), default="mysql")
    dialect: Mapped[str] = mapped_column(String(32), default="mysql")
    host: Mapped[str] = mapped_column(String(255))
    port: Mapped[int] = mapped_column(Integer, default=3306)
    database_name: Mapped[str] = mapped_column(String(255))
    username: Mapped[str] = mapped_column(String(255))
    encrypted_password: Mapped[str] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(32), default="pending")
    engine_version: Mapped[str | None] = mapped_column(String(100), nullable=True)
    capabilities: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)


class Conversation(WorkspaceResourceMixin, Base):
    __tablename__ = "conversations"
    title: Mapped[str] = mapped_column(String(300), default="New conversation")
    created_by: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"))


class Message(WorkspaceResourceMixin, Base):
    __tablename__ = "messages"
    __table_args__ = (Index("ix_messages_conversation_created", "conversation_id", "created_at"),)
    conversation_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("conversations.id", ondelete="CASCADE"))
    role: Mapped[str] = mapped_column(String(32))
    content: Mapped[str] = mapped_column(Text)


class AnalysisRun(WorkspaceResourceMixin, Base):
    __tablename__ = "analysis_runs"
    conversation_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("conversations.id", ondelete="SET NULL"), nullable=True)
    datasource_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("datasources.id", ondelete="SET NULL"), nullable=True, index=True)
    status: Mapped[str] = mapped_column(String(32), default="pending")
    question: Mapped[str] = mapped_column(Text)
    result: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)


class SchemaSnapshot(WorkspaceResourceMixin, Base):
    __tablename__ = "schema_snapshots"
    __table_args__ = (UniqueConstraint("datasource_id", "version", name="uq_schema_snapshots_datasource_version"),)
    datasource_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("datasources.id", ondelete="CASCADE"), index=True)
    schema_data: Mapped[dict[str, Any]] = mapped_column(JSON)
    version: Mapped[int] = mapped_column(Integer, default=1)


__all__ = [
    "AnalysisRun", "AuthSession", "AuthSessionFamily", "Base", "Conversation", "DataSource", "Message",
    "SchemaSnapshot", "User", "Workspace", "WorkspaceMember", "WorkspaceRole",
]
