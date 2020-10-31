from dataclasses import dataclass
from datetime import date, datetime
import re
from typing import List, Optional
from uuid import UUID, uuid4
from pydantic import BaseModel, Field, validator
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

    @validator("name")
    def check_name_length(cls, name):
        if len(name) > 32:
            raise ValueError("name must be no more than 32 characters.")

        return name

    @validator("name")
    def name_must_be_alphabetic_chars_and_space(cls, name):
        name_ = name.replace(" ", "")
        if not name_.isalpha():
            raise ValueError("name must be alphabetic characters.")

        return name

    @validator("email")
    def check_email_format(cls, email):
        match = re.fullmatch(r"^\w+[.\w]+\w@(\w+\.)+([a-z]+)$", email)
        if not match:
            raise ValueError("the value is not email format.")

        return email

    @validator("hobbies", pre=True)
    def split_hobby_string_by_comma(cls, hobbies):
        if isinstance(hobbies, str):
            return hobbies.split(",")

        return hobbies

    @validator("hobbies", each_item=True)
    def hobbies_is_not_empty(cls, hobby):
        if hobby.strip() == "":
            raise ValueError("hobby must not be empty string.")

        return hobby


Base = declarative_base()


class UserTable(Base):
    __tablename__ = "users"
    id = Column(String(36), primary_key=True, nullable=False)
    name = Column(String(64), nullable=False)
    email = Column(String(256), nullable=True)
    hobbies = Column(ARRAY(String(32)), nullable=False)
    activate_date = Column(Date, nullable=False)
    created_at = Column(TIMESTAMP, nullable=False)


@dataclass
class UserCreateRequest:
    name: str
    email: Optional[str]
    hobbies: List[str]
    activate_date: date


class Term(BaseModel):
    start: date
    end: date

    @validator("end")
    def end_date_must_be_later_than_start_date(cls, end, values):
        if "start" in values and values["start"] > end:
            raise ValueError("end date must be later than start date.")
        return end
