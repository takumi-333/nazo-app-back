import uuid
from sqlalchemy import Column, VARCHAR, ForeignKey
from sqlalchemy.dialects.postgresql import UUID

from app.core.database import Base


class Answer(Base):
    __tablename__ = "answers"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    riddle_id = Column(UUID(as_uuid=True), ForeignKey("riddles.id", ondelete="CASCADE"), nullable=False)
    answer_text = Column(VARCHAR, nullable=False)