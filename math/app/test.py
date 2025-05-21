import pytest
import requests

BASE_URL = "http://127.0.0.1:8000"
HEADERS = {"Authorization": "Bearer super-secret-token"}
INVALID_HEADERS = {"Authorization": "Bearer wrong-token"}

@pytest.mark.parametrize("endpoint,a,b,expected", [
    ("add", 10, 5, 15),
    ("subtract", 10, 5, 5),
    ("multiply", 10, 5, 50),
    ("divide", 10, 5, 2),
])
def test_math_operations(endpoint, a, b, expected):
    res = requests.post(
        f"{BASE_URL}/{endpoint}",
        json={"a": a, "b": b},
        headers=HEADERS
    )
    assert res.status_code == 200
    body = res.json()
    assert body["result"] == expected
    assert body["operation"] == endpoint
    assert body["a"] == a
    assert body["b"] == b

def test_divide_by_zero():
    res = requests.post(
        f"{BASE_URL}/divide",
        json={"a": 10, "b": 0},
        headers=HEADERS
    )
    assert res.status_code == 400
    assert res.json()["detail"] == "Division by zero is not allowed"

def test_auth_required():
    res = requests.post(
        f"{BASE_URL}/add",
        json={"a": 1, "b": 2}
    )
    assert res.status_code == 403
    assert res.json()["detail"] == "Not authenticated"

def test_invalid_token():
    res = requests.post(
        f"{BASE_URL}/add",
        json={"a": 1, "b": 2},
        headers={"Authorization": "Bearer wrong-token"}
    )
    assert res.status_code == 403
    assert res.json()["detail"] in ["Invalid or missing token", "Not authenticated"]


def test_invalid_payload_missing_field():
    res = requests.post(
        f"{BASE_URL}/add",
        json={"a": 5},
        headers=HEADERS
    )
    assert res.status_code == 422
    data = res.json()
    assert data["detail"][0]["type"] == "missing"
    assert data["detail"][0]["loc"] == ["body", "b"]
    assert "Field required" in data["detail"][0]["msg"]



def test_invalid_payload_wrong_type():
    res = requests.post(
        f"{BASE_URL}/multiply",
        json={"a": "hello", "b": 5},
        headers=HEADERS
    )
    assert res.status_code == 422
    data = res.json()
    assert data["detail"][0]["type"] == "float_parsing"
    assert data["detail"][0]["loc"] == ["body", "a"]
    assert "unable to parse" in data["detail"][0]["msg"]


if __name__ == "__main__":
    pytest.main()