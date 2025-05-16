from datetime import datetime
from typing import List, Optional, Type

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from ninja_extra import status
from ninja_extra.exceptions import APIException
from ninja import Schema, ModelSchema
from pydantic import field_validator

UserModel = get_user_model()


class GroupSchema(ModelSchema):
    class Meta:
        model = Group
        fields = ("name",)


class UserRetrieveSchema(ModelSchema):
    groups: List[GroupSchema]

    class Meta:
        model = UserModel
        fields = ("first_name", "last_name", "username", "id", "is_active")


class UserTokenOutSchema(Schema):
    token: str
    user: UserRetrieveSchema
    token_exp_date: Optional[datetime]
