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

        case TestTypeEnum.KEYCLOAK:
            payload = {
                "client_id": service_conf.client_id,
                "grant_type": "password",
                "username": user.email,
                "password": user.password,
            }

        case _:
            raise ValueError(f"Unknown test type: {service_conf.auth_type}")

    headers = {"Content-Type": "application/json"}
    response = requests.post(service_conf.login_url, json=payload, headers=headers)

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
            client_id=s["client_id"],
        )

    users = {}
    for key, u in data["users"].items():
        users[key] = User(
            email=u["email"], password=u["password"], role=UserRoleEnum[u["role"]]
        )

    scenarios = []
    for sc in data["scenarios"]:
        service = services[sc["service_id"]]
        user_key = sc.get("user_id")

        if user_key:
            user = users.get(user_key)

            if not user:
                raise ValueError(f"User with key {user_key} not found")
        else:
            user = None

        body = sc.get("body", {})

        scenarios.append(
            (
                sc["scenario_name"],
                service,
                user,
                sc["method"],
                sc["endpoint"],
                sc["expected_status"],
                body,
            )
        )

    return scenarios
