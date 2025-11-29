import pytest
import requests

from .util.helpers import load_test_data ,get_token

TEST_SCENARIOS = load_test_data()

@pytest.mark.parametrize("service, user, method, endpoint, expected_status, body", TEST_SCENARIOS)
def test_api_security(service, user, method, endpoint, expected_status, body={}):
    headers = {
        "Content-Type": "application/json"
    }
    url = f"{service.base_url}{endpoint}"

    if user:
        token = get_token(service, user)
        headers["Authorization"] = f"Bearer {token}"

    response = requests.request(method, url, headers=headers, json=body)

    user_string = f"{user.email} ({user.role.name}" if user else "Unauthorized"
    assert response.status_code == expected_status, (
        f"\nService: {service.name} ({service.auth_type.name})"
        f"\nUser: {user_string})"
        f"\nEndpoint: {method} {endpoint}"
        f"\nOczekiwano: {expected_status}, Otrzymano: {response.status_code}"
        f"\nResponse Body: {response.text[:200]}"
    )