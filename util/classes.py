from enum import Enum
from dataclasses import dataclass


@dataclass
class ServiceConfig:
    name: str
    base_url: str
    auth_type: TestTypeEnum
    login_url: str
    client_id: str = ""

    def get_url(self, endpoint: str):
        clean_base = self.base_url.rstrip("/")
        clean_endpoint = endpoint.lstrip("/").rstrip("/")
        return f"{clean_base}/{clean_endpoint}/"


@dataclass
class User:
    email: str
    password: str
    role: UserRoleEnum


class TestTypeEnum(Enum):
    SIMPLE_JWT = 1
    KEYCLOAK = 2


class UserRoleEnum(Enum):
    BOOK_USER = 1
    BOOK_ADMIN = 2
