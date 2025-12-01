import requests
import json

from pydantic import ValidationError
from .classes import ServiceConfig, User, TestTypeEnum, TestScenario


def get_token(service_conf: ServiceConfig, user: User):
    match service_conf.auth_type:
        case TestTypeEnum.SIMPLE_JWT:
            payload = {
                "email": user.email,
                "password": user.password,
            }
            headers = {"Content-Type": "application/json"}
            response = requests.post(
                service_conf.login_url, json=payload, headers=headers
            )

        case TestTypeEnum.KEYCLOAK:
            payload = {
                "client_id": service_conf.client_id,
                "grant_type": "password",
                "username": user.email,
                "password": user.password,
            }
            headers = {"Content-Type": "application/x-www-form-urlencoded"}
            response = requests.post(
                service_conf.login_url, data=payload, headers=headers
            )

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
    try:
        for key, s_data in data["services"].items():
            services[key] = ServiceConfig(**s_data)

        users = {}
        for key, u_data in data["users"].items():
            users[key] = User(**u_data)

        final_scenarios = []
        for _, service in services.items():
            for key, s_data in data["scenarios"].items():
                scenario = TestScenario(*s_data)
                user_key = scenario.user_id

                if user_key:
                    user = users.get(user_key)

                    if not user:
                        raise ValueError(f"User with key {user_key} not found")
                else:
                    user = None

                body = scenario.body

                base_name = (
                    scenario.name
                    if scenario.name
                    else f"{scenario.method}/{scenario.endpoint}"
                )
                full_scenario_name = f"[{service.name}] {base_name}"
                final_scenarios.append(
                    (
                        full_scenario_name,
                        service,
                        user,
                        scenario.method,
                        scenario.endpoint,
                        scenario.expected_status,
                        body,
                    )
                )
    except ValidationError as e:
        print("BŁĄD KONFIGURACJI JSON!")
        print(e.json())
        raise e

    return final_scenarios
