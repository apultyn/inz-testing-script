import requests
import json

from .classes import ServiceConfig, User, TestTypeEnum, UserRoleEnum


def get_token(service_conf: ServiceConfig, user: User):
    match service_conf.auth_type:
        case TestTypeEnum.SIMPLE_JWT:
            payload = {
                "email": user.email,
                "password": user.password,
            }

            response = requests.post(service_conf.login_url, data=payload)

        case TestTypeEnum.KEYCLOAK:
            payload = {
                "client_id": service_conf.client_id,
                "grant_type": "password",
                "username": user.email,
                "password": user.password,
            }
            response = requests.post(service_conf.login_url, json=payload)

        case _:
            raise ValueError(f"Unknown test type: {service_conf.auth_type}")

    if response.status_code != 200:
        raise Exception(
            f"Error logging to {service_conf.name} as {user.role}: {response.text}"
        )

    data = response.json()
    return data.get("access_token") or data.get("token")


def load_test_data():
    with open("test_config.json", "r") as file_handle:
        data = json.load(file_handle)

    services = {}
    for key, s in data["services"].items():
        services[key] = ServiceConfig(
            name=s["name"],
            base_url=s["base_url"],
            auth_type=TestTypeEnum[s["auth_type"]],
            login_url=s["login_url"],
            client_id=s["client_id"]
        )

    users = {}
    for key, u in data["users"].items():
        users[key] = User(
            email=u["email"],
            password=u["password"],
            role=UserRoleEnum[u["role"]]
        )

    scenarios = []
    for sc in data["scenarios"]:
        service = services[sc["service_id"]]
        user = users[sc["user_id"]]
        scenarios.append((
            service,
            user,
            sc["method"],
            sc["endpoint"],
            sc["expected_status"],
            sc["body"]
        ))

    return scenarios