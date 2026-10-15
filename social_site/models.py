from datetime import datetime
from enum import Enum
from typing import Optional

from .db import Base

from sqlalchemy import CheckConstraint, Column, DateTime, ForeignKey, Integer, LargeBinary, String, Table, Text, Boolean, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

# Association tables

topic_member_association_table = Table(
    "topic_member_association_table",
    Base.metadata,
    Column("user_id", Integer, ForeignKey("user.id"), primary_key=True),
    Column("topic_id", Integer, ForeignKey("topic.id"), primary_key=True),
)

tags_association_table = Table(
    "tags_association_table",
    Base.metadata,
    Column("tag_id", Integer, ForeignKey("tag.id"), primary_key=True),
    Column("post_id", Integer, ForeignKey("post.id"), primary_key=True),
)

chat_association_table = Table(
    "chat_association_table",
    Base.metadata,
    Column("chat_id", Integer, ForeignKey("chat.id"), primary_key=True),
    Column("user_id", Integer, ForeignKey("user.id"), primary_key=True),
)

# Tables

class User(Base):
    __tablename__ = "user"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(
        String(30), unique=True, nullable=False
    )
    display_name: Mapped[str] = mapped_column(
        String(30), nullable=False
    )
    email: Mapped[str] = mapped_column(
        String(255), unique=True, nullable=False
    )
    password_hash: Mapped[str] = mapped_column(
        Text, nullable=False
    )
    profile_picture: Mapped[Optional[bytes]] = mapped_column(
        LargeBinary, nullable=True
    )

    # Relations
    posts: Mapped[list["Post"]] = relationship(back_populates="user")
    topics: Mapped[list["Topic"]] = relationship(secondary=topic_member_association_table, back_populates="members")
    replies: Mapped[list["Reply"]] = relationship(back_populates="user")
    reactions: Mapped[list["Reaction"]] = relationship(back_populates="user")
    settings: Mapped["UserSettings | None"] = relationship(back_populates="user", cascade="all, delete-orphan")
    messages: Mapped[list["ChatMessage"]] = relationship(back_populates="user")
    chats: Mapped[list["Chat"]] = relationship(
        secondary=chat_association_table, back_populates="members"
    )

    def __init__(self, username: str, display_name: str, email: str, password_hash: str):
        self.username = username
        self.display_name = display_name
        self.email = email
        self.password_hash = password_hash

class UserSettings(Base):
    __tablename__ = "user_settings"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), unique=True, nullable=False)
    user: Mapped["User"] = relationship(back_populates="settings")

    # Settings
    theme: Mapped[str] = mapped_column(String(50), default="system")
    enable_animations: Mapped[bool] = mapped_column(Boolean(), default=True, nullable=False)
    show_online_status: Mapped[bool] = mapped_column(Boolean(), default=True, nullable=False)
    profile_private: Mapped[bool] = mapped_column(Boolean(), default=True, nullable=False)
    mention_notifications: Mapped[bool] = mapped_column(Boolean(), default=True, nullable=False)
    followed_notifications: Mapped[bool] = mapped_column(Boolean(), default=True, nullable=False)

class Topic(Base):
    __tablename__ = "topic"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    posts: Mapped[list["Post"]] = relationship(back_populates="topic")
    members: Mapped[list["User"]] = relationship(secondary=topic_member_association_table, back_populates="topics")

    description: Mapped[str] = mapped_column(String(9999), nullable=False)
    image: Mapped[Optional[bytes]] = mapped_column(LargeBinary, nullable=True)

class Tag(Base):
    __tablename__ = "tag"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    posts: Mapped[list["Post"]] = relationship(secondary=tags_association_table, back_populates="tags")

class Post(Base):
    __tablename__ = "post"

    id: Mapped[int] = mapped_column(primary_key=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.current_timestamp(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=True,
        onupdate=func.current_timestamp(),
    )

    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), nullable=False)
    user: Mapped["User"] = relationship(back_populates="posts")

    topic_id: Mapped[int] = mapped_column(ForeignKey("topic.id"), nullable=False)
    topic: Mapped["Topic"] = relationship(back_populates="posts")

    tags: Mapped[list["Tag"]] = relationship(secondary=tags_association_table, back_populates="posts")

    replies: Mapped[list["Reply"]] = relationship(back_populates="post")
    reactions: Mapped[list["Reaction"]] = relationship(back_populates="post")

    # Post data
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    body: Mapped[Optional[str | None]] = mapped_column(Text, nullable=True)
    href: Mapped[Optional[str | None]] = mapped_column(Text, nullable=True)
    image: Mapped[Optional[str | None]] = mapped_column(Text, nullable=True)

class Reply(Base):
    __tablename__ = "reply"

    id: Mapped[int] = mapped_column(primary_key=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.current_timestamp(),
        nullable=False,
    )

    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), nullable=False)
    user: Mapped["User"] = relationship(back_populates="replies")

    post_id: Mapped[int] = mapped_column(ForeignKey("post.id"), nullable=False)
    post: Mapped["Post"] = relationship(back_populates="replies")

    reactions: Mapped[list["Reaction"]] = relationship(back_populates="reply")

    parent_id: Mapped[Optional[int | None]] = mapped_column(ForeignKey("reply.id"), nullable=True)
    parent: Mapped["Reply | None"] = relationship(back_populates="children", remote_side="Reply.id")
    children: Mapped[list["Reply"]] = relationship(back_populates="parent")

    # Reply data
    text: Mapped[str] = mapped_column(String(1000), nullable=False)

class ReactionType(Enum):
    LIKE = 1
    DISLIKE = 0

class Reaction(Base):
    __tablename__ = "reaction"

    
    __table_args__ = (
        CheckConstraint(
            "(post_id IS NOT NULL AND reply_id IS NULL) OR "
            "(post_id IS NULL AND reply_id IS NOT NULL)",
            name="ck_reaction_exactly_one_target",
        ),
        UniqueConstraint(
            "user_id", "post_id",
            name="uq_reaction_user_post",
        ),
        UniqueConstraint(
            "user_id", "reply_id",
            name="uq_reaction_user_reply",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    type: Mapped["ReactionType"] # According to the SQLAlchemy docs, excluding `mapped_column` is perfectly valid - the type annotation fills it in

    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), nullable=False)
    user: Mapped["User"] = relationship(back_populates="reactions")

    post_id: Mapped[Optional[int | None]] = mapped_column(ForeignKey("post.id"), nullable=True)
    post: Mapped["Post | None"] = relationship(back_populates="reactions")

    reply_id: Mapped[Optional[int | None]] = mapped_column(ForeignKey("reply.id"), nullable=True)
    reply: Mapped["Reply | None"] = relationship(back_populates="reactions")

class Chat(Base):
    __tablename__ = "chat"

    id: Mapped[int] = mapped_column(primary_key=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.current_timestamp(),
        nullable=False,
    )

    title: Mapped[str] = mapped_column(String(100), nullable=False)
    
    members: Mapped[list["User"]] = relationship(
        secondary=chat_association_table, back_populates="chats"
    )

    messages: Mapped[list["ChatMessage"]] = relationship(back_populates="chat")

class ChatMessage(Base):
    __tablename__ = "chat_message"

    id: Mapped[int] = mapped_column(primary_key=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.current_timestamp(),
        nullable=False,
    )

    chat_id: Mapped[int] = mapped_column(ForeignKey("chat.id"))
    chat: Mapped["Chat"] = relationship(back_populates="messages")

    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"))
    user: Mapped["User"] = relationship(back_populates="messages")

    text: Mapped[str] = mapped_column(String(250), nullable=False)