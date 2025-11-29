import pytest
import requests

from util.helpers import load_test_data, get_token
from util.classes import ServiceConfig, User

TEST_SCENARIOS = load_test_data()


@pytest.mark.parametrize(
    "scenatio_name, service, user, method, endpoint, expected_status, body",
    TEST_SCENARIOS,
)
def test_api_security(
    scenatio_name: str,
    service: ServiceConfig,
    user: User,
    method: str,
    endpoint: str,
    expected_status: type[int],
    body,
):
    headers = {"Content-Type": "application/json"}
    url = service.get_url(endpoint)

    if user:
        token = get_token(service, user)
        headers["Authorization"] = f"Bearer {token}"

    response = requests.request(method, url, headers=headers, json=body)

    user_string = f"{user.email} ({user.role.name}" if user else "Unauthenticated user"
    assert response.status_code in expected_status, (
        f"\nScenario Name: {scenatio_name}"
        f"\nService: {service.name} ({service.auth_type.name})"
        f"\nUser: {user_string})"
        f"\nEndpoint: {method} {endpoint}"
        f"\nExpected: {expected_status}, Received: {response.status_code}"
        f"\nResponse Body: {response.text[:200]}"
    )
