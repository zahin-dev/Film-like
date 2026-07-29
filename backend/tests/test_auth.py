"""Authentication and Japanese error-contract tests."""


VALID_USER = {
    "first_name": "太郎",
    "last_name": "映画",
    "email": "taro@example.com",
    "password": "Test1234!",
    "age": 24,
}


def test_app_starts_without_cloud_api_keys(client):
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {
        "message": "Film-like 日本語版 API は稼働中です。",
        "locale": "ja-JP",
        "region": "JP",
        "timezone": "Asia/Tokyo",
    }


def test_openapi_metadata_is_japanese_and_local(client):
    document = client.get("/openapi.json").json()
    assert document["info"]["title"] == "Film-like 日本語版 API"
    assert "クラウド映画API" in document["info"]["description"]
    assert {tag["name"] for tag in document["tags"]} == {
        "認証",
        "映画",
        "タグ",
        "分析",
        "推薦",
        "システム",
    }
    assert document["paths"]["/"]["get"]["tags"] == ["システム"]
    rendered = str(document)
    assert "Personal film diary API with TMDB integration" not in rendered
    assert "Mistral AI" not in rendered


def test_register_and_login(client):
    registered = client.post("/auth/register", json=VALID_USER)
    assert registered.status_code == 201
    assert registered.json()["user"]["username"] == "太郎映画"
    assert registered.json()["token"]

    logged_in = client.post(
        "/auth/login",
        json={"email": VALID_USER["email"], "password": VALID_USER["password"]},
    )
    assert logged_in.status_code == 200
    assert logged_in.json()["user"]["email"] == VALID_USER["email"]


def test_duplicate_email_returns_japanese_conflict(client):
    assert client.post("/auth/register", json=VALID_USER).status_code == 201
    response = client.post("/auth/register", json=VALID_USER)
    assert response.status_code == 409
    assert response.json()["detail"] == (
        "このメールアドレスはすでに登録されています。"
    )


def test_invalid_login_does_not_reveal_account_existence(client):
    response = client.post(
        "/auth/login",
        json={"email": "unknown@example.com", "password": "Wrong123!"},
    )
    assert response.status_code == 401
    assert response.json()["detail"] == (
        "メールアドレスまたはパスワードが正しくありません。"
    )


def test_password_validation_is_japanese(client):
    payload = {**VALID_USER, "email": "weak@example.com", "password": "abcdefgh"}
    response = client.post("/auth/register", json=payload)
    assert response.status_code == 422
    assert "数字を1文字以上" in response.json()["detail"][0]["msg"]


def test_missing_required_field_is_japanese(client):
    payload = {key: value for key, value in VALID_USER.items() if key != "email"}
    response = client.post("/auth/register", json=payload)
    assert response.status_code == 422
    assert response.json()["detail"][0]["msg"] == (
        "メールアドレスは必須です。"
    )


def test_protected_route_requires_login_in_japanese(client):
    response = client.get("/films/history")
    assert response.status_code == 401
    assert response.json()["detail"] == "ログインが必要です。"
