import uuid
from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, ForeignKey, Index, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database_sql import Base


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def uuid_string() -> str:
    return str(uuid.uuid4())


class Participant(Base):
    __tablename__ = "participants"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid_string)
    participant_id: Mapped[str] = mapped_column(String(320), unique=True, index=True, nullable=False)
    user_index: Mapped[int] = mapped_column(Integer, unique=True, index=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)
    last_seen_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)

    conversations: Mapped[list["Conversation"]] = relationship(back_populates="participant")


class Conversation(Base):
    __tablename__ = "conversations"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    participant_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("participants.id", ondelete="RESTRICT"),
        index=True,
        nullable=False,
    )
    modality_group: Mapped[str] = mapped_column(String(32), index=True, nullable=False)
    modality_selected_client_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    source_system: Mapped[str] = mapped_column(String(32), index=True, nullable=False)
    selection_reason: Mapped[str] = mapped_column(Text, default="", nullable=False)
    selection_reason_client_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    status: Mapped[str] = mapped_column(String(24), default="in_progress", index=True, nullable=False)
    question_code: Mapped[str] = mapped_column(String(32), default="HEX", nullable=False)
    question_sequence: Mapped[str] = mapped_column(Text, default="[]", nullable=False)
    questions_answered: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    participant: Mapped[Participant] = relationship(back_populates="conversations")
    messages: Mapped[list["Message"]] = relationship(
        back_populates="conversation",
        cascade="all, delete-orphan",
        order_by="Message.sequence_number",
    )
    audio_recordings: Mapped[list["AudioRecording"]] = relationship(back_populates="conversation")


class Message(Base):
    __tablename__ = "messages"
    __table_args__ = (
        UniqueConstraint("conversation_id", "sequence_number", name="uq_message_sequence"),
        UniqueConstraint("conversation_id", "client_message_id", name="uq_client_message"),
        Index("ix_messages_conversation_created", "conversation_id", "server_received_at"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid_string)
    conversation_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("conversations.id", ondelete="CASCADE"),
        nullable=False,
    )
    sequence_number: Mapped[int] = mapped_column(Integer, nullable=False)
    role: Mapped[str] = mapped_column(String(16), index=True, nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    raw_user_input: Mapped[str | None] = mapped_column(Text, nullable=True)
    raw_transcript: Mapped[str | None] = mapped_column(Text, nullable=True)
    input_method: Mapped[str | None] = mapped_column(String(32), nullable=True)
    client_message_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    client_created_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    server_received_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)
    timestamp_source: Mapped[str] = mapped_column(String(24), default="server", nullable=False)
    processing_completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    processing_status: Mapped[str] = mapped_column(String(24), default="completed", nullable=False)
    metadata_json: Mapped[str | None] = mapped_column(Text, nullable=True)

    conversation: Mapped[Conversation] = relationship(back_populates="messages")
    audio_recordings: Mapped[list["AudioRecording"]] = relationship(
        back_populates="message",
        order_by="AudioRecording.uploaded_at",
    )


class AudioRecording(Base):
    __tablename__ = "audio_recordings"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid_string)
    conversation_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("conversations.id", ondelete="RESTRICT"),
        index=True,
        nullable=False,
    )
    participant_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("participants.id", ondelete="RESTRICT"),
        index=True,
        nullable=False,
    )
    file_path: Mapped[str] = mapped_column(Text, unique=True, nullable=False)
    original_filename: Mapped[str | None] = mapped_column(Text, nullable=True)
    mime_type: Mapped[str | None] = mapped_column(String(128), nullable=True)
    byte_size: Mapped[int] = mapped_column(Integer, nullable=False)
    sha256: Mapped[str] = mapped_column(String(64), nullable=False)
    raw_transcript: Mapped[str | None] = mapped_column(Text, nullable=True)
    upload_started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    uploaded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)
    timestamp_source: Mapped[str] = mapped_column(String(24), default="server", nullable=False)
    transcribed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    transcription_succeeded: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    message_id: Mapped[str | None] = mapped_column(
        String(36),
        ForeignKey("messages.id", ondelete="SET NULL"),
        index=True,
        nullable=True,
    )

    conversation: Mapped[Conversation] = relationship(back_populates="audio_recordings")
    message: Mapped[Message | None] = relationship(
        back_populates="audio_recordings",
        foreign_keys=[message_id],
        uselist=False,
    )
