from fastapi.testclient import TestClient

from src.main import app

client = TestClient(app)


def test_post_get_url():
    url = "https://google.com"

    post_response = client.post("/", json={"url": url})
    post_json = post_response.json()

    assert post_response.status_code == 201
    assert len(post_json["_id"]) == 6

    get_response = client.get("/" + post_json["_id"])
    assert get_response.status_code != 404
