import uuid
from sqlalchemy import Boolean, Column, Integer, Text, VARCHAR, ForeignKey, text, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
 
from app.core.database import Base
 
 
class Riddle(Base):
    __tablename__ = "riddles"
 
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    # creator_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    creator_id = Column(UUID(as_uuid=True), nullable=True)
    image_url = Column(Text, nullable=False)
    explanation = Column(Text, nullable=True)
    status = Column(VARCHAR, nullable=False, default="draft")
    play_count = Column(Integer, nullable=False, default=0)
    has_hint = Column(Boolean, nullable=False, default=False)
    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("now()"),
    )

    updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("now()"),
        onupdate=func.now(),
    )
 