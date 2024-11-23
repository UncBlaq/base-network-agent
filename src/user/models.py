from sqlalchemy import Column, String
from sqlalchemy.dialects.postgresql import UUID
import uuid

from database import Base

class Subscribers(Base):

    __tablename__ = 'subscribers'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    email = Column(String, unique=True, nullable = False)