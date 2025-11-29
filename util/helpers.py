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
            headers = {"Content-Type": "application/json"}
            response = requests.post(service_conf.login_url, json=payload, headers=headers)

        case TestTypeEnum.KEYCLOAK:
            payload = {
                "client_id": service_conf.client_id,
                "grant_type": "password",
                "username": user.email,
                "password": user.password,
            }
            headers = {
                "Content-Type": "application/x-www-form-urlencoded"
            }
            response = requests.post(service_conf.login_url, data=payload, headers=headers)

        case _:
            raise ValueError(f"Unknown test type: {service_conf.auth_type}")

    if response.status_code != 200:
        raise Exception(
            f"Error logging to {service_conf.name} as {user.role}: {response.text}"
        )

    data = response.json()
    return data.get("access_token") or data.get("token") or data.get("access")


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

    final_scenarios = []
    for _, service in services.items():
        for sc in data["scenarios"]:
            user_key = sc.get("user_id")

            if user_key:
                user = users.get(user_key)

                if not user:
                    raise ValueError(f"User with key {user_key} not found")
            else:
                user = None

            body = sc.get("body", {})

            base_name = sc.get("name", f"{sc['method']} {sc['endpoint']}")
            full_scenario_name = f"[{service.name}] {base_name}"
            final_scenarios.append(
                (
                    full_scenario_name,
                    service,
                    user,
                    sc["method"],
                    sc["endpoint"],
                    sc["expected_status"],
                    body,
                )
            )

    return final_scenarios
