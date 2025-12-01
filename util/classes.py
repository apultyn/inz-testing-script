from enum import Enum
from pydantic import BaseModel, Field
from typing import Dict, List


class TestTypeEnum(str, Enum):
    SIMPLE_JWT = "SIMPLE_JWT"
    KEYCLOAK = "KEYCLOAK"


class UserRoleEnum(str, Enum):
    BOOK_USER = "BOOK_USER"
    BOOK_ADMIN = "BOOK_ADMIN"


class ServiceConfig(BaseModel):
    name: str
    base_url: str
    auth_type: TestTypeEnum
    login_url: str
    client_id: str

    def get_url(self, endpoint: str):
        clean_base = self.base_url.rstrip("/")
        clean_endpoint = endpoint.lstrip("/").rstrip("/")
        return f"{clean_base}/{clean_endpoint}/"


class User(BaseModel):
    email: str
    password: str
    role: UserRoleEnum


class TestScenario(BaseModel):
    scenario_name: str
    user_id: str
    method: str
    endpoint: str
    expected_status: List[int]
    body: Dict = Field(default_factory=dict)
