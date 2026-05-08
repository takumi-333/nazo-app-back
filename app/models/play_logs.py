import uuid
from sqlalchemy import Column, Boolean, Integer, ForeignKey, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.core.database import Base


class PlayLog(Base):
    __tablename__ = "play_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    riddle_id = Column(UUID(as_uuid=True), ForeignKey("riddles.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    correct = Column(Boolean, nullable=False)
    duration_ms = Column(Integer, nullable=True)
    used_hint = Column(Boolean, nullable=False, default=False)
    attempt_count = Column(Integer, nullable=True)
    created_at = Column(server_default=text("now()"), nullable=False)

    rating = relationship("Rating", back_populates="play_log", uselist=False)