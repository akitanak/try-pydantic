from datetime import date, datetime
from typing import List, Optional
from uuid import UUID, uuid4
from pydantic import BaseModel, Field
from sqlalchemy import Column, Date, String, TIMESTAMP
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.ext.declarative import declarative_base


class User(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    name: str
    email: Optional[str]
    hobbies: List[str]
    activate_date: date
    created_at: datetime = Field(default_factory=datetime.now)

    class Config:
        orm_mode = True


Base = declarative_base()


class UserTable(Base):
    __tablename__ = "users"
    id = Column(String(36), primary_key=True, nullable=False)
    name = Column(String(64), nullable=False)
    email = Column(String(256), nullable=True)
    hobbies = Column(ARRAY(String(32)), nullable=False)
    activate_date = Column(Date, nullable=False)
    created_at = Column(TIMESTAMP, nullable=False)
