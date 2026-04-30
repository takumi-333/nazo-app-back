import uuid
from sqlalchemy import Column, String, DateTime, text
from sqlalchemy.dialects.postgresql import UUID
from app.core.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        server_default=text("gen_random_uuid()"),
    )
    username = Column(String, nullable=False, unique=True, index=True)
    password_hash = Column(String, nullable=False)
    email = Column(String, nullable=True, unique=True, index=True)
    avatar_url = Column(String, nullable=True)
    role = Column(String, nullable=False, server_default="user")
    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("now()"),
    )