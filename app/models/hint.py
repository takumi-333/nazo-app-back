import uuid
from sqlalchemy import Column, Text, ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID

from app.core.database import Base


class Hint(Base):
    __tablename__ = "hints"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    riddle_id = Column(UUID(as_uuid=True), ForeignKey("riddles.id", ondelete="CASCADE"), nullable=False)
    content = Column(Text, nullable=False)

    __table_args__ = (
        UniqueConstraint("riddle_id", name="uq_hints_riddle_id"),  # 1問につき1件のみ
    )