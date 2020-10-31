from datetime import date, datetime, timedelta
from uuid import uuid4
from pydantic import ValidationError
import pytest
from try_pydantic.sample import Term, User, UserCreateRequest, UserTable


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
        name="p" * 33,
        email="pat@example.com",
        hobbies=["reading book", "play the guitar"],
        activate_date=date.today(),
    )

    with pytest.raises(ValidationError) as ex:
        User.from_orm(user_create_request)


def test_name_characters_check():
    user_create_request = UserCreateRequest(
        name="patric s1natra",
        email="pat@example.com",
        hobbies=["reading book", "play the guitar"],
        activate_date=date.today(),
    )

    with pytest.raises(ValidationError) as ex:
        User.from_orm(user_create_request)


def test_name_has_some_errors():
    user_create_request = UserCreateRequest(
        name="patric s1natra" * 3,
        email="pat@example.com",
        hobbies=["reading book", "play the guitar"],
        activate_date=date.today(),
    )

    with pytest.raises(ValidationError) as ex:
        User.from_orm(user_create_request)

    errors = ex.value.errors()
    # プロパティに対して複数のバリデータが設定されていた場合、
    # 定義順で実行され、エラーになったところで返ってくる。
    assert len(errors) == 1
    assert errors[0]["loc"] == ("name",)
    assert errors[0]["msg"] == "name must be no more than 32 characters."


def test_some_property_have_errors():
    user_create_request = UserCreateRequest(
        name="patric s1natra",
        email="pat@example",
        hobbies=["reading book", "play the guitar"],
        activate_date=date.today(),
    )

    with pytest.raises(ValidationError) as ex:
        User.from_orm(user_create_request)

    errors = ex.value.errors()
    # 複数プロパティにバリデータが設定されていて、複数プロパティでバリデーションエラーになった場合、
    # 定義順で実行され、それぞれのプロパティのエラーが返ってくる。
    assert len(errors) == 2
    assert errors[0]["loc"] == ("name",)
    assert errors[0]["msg"] == "name must be alphabetic characters."
    assert errors[1]["loc"] == ("email",)
    assert errors[1]["msg"] == "the value is not email format."


def test_validator_can_preprocess_property():
    user_create_request = UserCreateRequest(
        name="patric sinatra",
        email="pat@example.com",
        hobbies="reading book,meditation,party,play the guitar",
        activate_date=date.today(),
    )

    user = User.from_orm(user_create_request)

    assert len(user.hobbies) == 4
    assert user.hobbies[0] == "reading book"
    assert user.hobbies[1] == "meditation"
    assert user.hobbies[2] == "party"
    assert user.hobbies[3] == "play the guitar"


def test_validate_each_list_elements():
    user_create_request = UserCreateRequest(
        name="patric sinatra",
        email="pat@example.com",
        hobbies=["reading book", "", "  "],
        activate_date=date.today(),
    )

    with pytest.raises(ValidationError) as ex:
        User.from_orm(user_create_request)

    errors = ex.value.errors()
    assert len(errors) == 2
    assert errors[0]["loc"] == ("hobbies", 1)
    assert errors[0]["msg"] == "hobby must not be empty string."
    assert errors[1]["loc"] == ("hobbies", 2)
    assert errors[1]["msg"] == "hobby must not be empty string."


def test_correlation_check():
    start = date.today()
    end = start + timedelta(days=1)

    term = Term(start=start, end=end)

    assert term.start == start
    assert term.end == end

    invalid_end = start - timedelta(days=1)

    with pytest.raises(ValidationError) as ex:
        Term(start=start, end=invalid_end)

    errors = ex.value.errors()
    assert len(errors) == 1
    assert errors[0]["loc"] == ("end",)
    assert errors[0]["msg"] == "end date must be later than start date."
