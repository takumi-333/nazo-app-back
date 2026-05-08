import uuid
from sqlalchemy import Column, Integer, ForeignKey, text, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.core.database import Base


class Rating(Base):
    __tablename__ = "ratings"

    __table_args__ = (
        UniqueConstraint("riddle_id", "user_id", name="uq_ratings_riddle_user"),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    play_log_id = Column(UUID(as_uuid=True), ForeignKey("play_logs.id", ondelete="CASCADE"), nullable=False)
    riddle_id = Column(UUID(as_uuid=True), ForeignKey("riddles.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    score = Column(Integer, nullable=False)
    created_at = Column(server_default=text("now()"), nullable=False)

    play_log = relationship("PlayLog", back_populates="rating")