from datetime import date, datetime
from uuid import uuid4
from pydantic import ValidationError
import pytest
from try_pydantic.sample import User, UserCreateRequest, UserTable


def test_create_user():

    user_attributes = {
        "name": "patric sinatra",
        "email": "pat@example.com",
        "hobbies": ["reading book", "play the guitar"],
        "activate_date": date.today(),
    }

    user = User(**user_attributes)

    assert user.id
    assert user.name == user_attributes["name"]
    assert user.email == user_attributes["email"]
    assert user.hobbies == user_attributes["hobbies"]
    assert user.activate_date == user_attributes["activate_date"]
    assert user.created_at


def test_create_user_from_orm_model():

    user_record = UserTable(
        id=str(uuid4()),
        name="patric sinatra",
        email="pat@example.com",
        hobbies=["reading book", "play the guitar"],
        activate_date=date.today(),
        created_at=datetime.utcnow(),
    )

    user = User.from_orm(user_record)

    assert str(user.id) == user_record.id
    assert user.name == user_record.name
    assert user.email == user_record.email
    assert user.hobbies == user_record.hobbies
    assert user.activate_date == user_record.activate_date
    assert user.created_at == user_record.created_at


def test_create_user_from_dataclass():
    """from_orm とは言うが、普通のdataclassからも変換できる。"""
    user_create_request = UserCreateRequest(
        name="patric sinatra",
        email="pat@example.com",
        hobbies=["reading book", "play the guitar"],
        activate_date=date.today(),
    )

    user = User.from_orm(user_create_request)

    assert user.id
    assert user.name == user_create_request.name
    assert user.email == user_create_request.email
    assert user.hobbies == user_create_request.hobbies
    assert user.activate_date == user_create_request.activate_date
    assert user.created_at


def test_name_length_check():
    user_create_request = UserCreateRequest(
        name="p" * 37,
        email="pat@example.com",
        hobbies=["reading book", "play the guitar"],
        activate_date=date.today(),
    )

    with pytest.raises(ValidationError) as ex:
        User.from_orm(user_create_request)

    print(ex)