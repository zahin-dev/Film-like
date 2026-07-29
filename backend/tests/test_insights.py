"""Deterministic Japanese diary-insight tests."""


def _log(client, headers, film_id, tag_ids):
    response = client.post(
        "/films/log",
        json={"film_id": film_id, "tag_ids": tag_ids},
        headers=headers,
    )
    assert response.status_code == 201


def test_empty_diary_has_controlled_zero_summary(client, auth_headers):
    body = client.get("/insights", headers=auth_headers).json()
    assert body == {
        "total_films": 0,
        "tagged_films": 0,
        "unique_reaction_signals": 0,
        "top_reaction_signals": [],
        "recent_reaction_signals": [],
    }


def test_insights_return_japanese_tag_counts(
    client, auth_headers, demo_films
):
    tags = client.get("/tags").json()
    feel_good = next(tag for tag in tags if tag["key"] == "feel-good")
    heartwarming = next(tag for tag in tags if tag["key"] == "heartwarming")
    _log(
        client,
        auth_headers,
        demo_films[0].id,
        [feel_good["id"], heartwarming["id"]],
    )
    _log(
        client,
        auth_headers,
        demo_films[1].id,
        [feel_good["id"]],
    )
    _log(client, auth_headers, demo_films[2].id, [])

    body = client.get("/insights", headers=auth_headers).json()
    assert body["total_films"] == 3
    assert body["tagged_films"] == 2
    assert body["unique_reaction_signals"] == 2
    assert body["top_reaction_signals"] == [
        {"tag": "元気をもらえる", "count": 2, "percentage": 100.0},
        {"tag": "心が温まる", "count": 1, "percentage": 50.0},
    ]


def test_recent_insights_use_latest_five_entries(
    client, auth_headers, demo_films
):
    tags = client.get("/tags").json()
    first = next(tag for tag in tags if tag["key"] == "feel-good")
    recent = next(tag for tag in tags if tag["key"] == "terrifying")
    for index, film in enumerate(demo_films[:6]):
        _log(
            client,
            auth_headers,
            film.id,
            [first["id"]] if index == 0 else [recent["id"]],
        )

    body = client.get("/insights", headers=auth_headers).json()
    assert body["recent_reaction_signals"] == [
        {"tag": "本気で怖い", "count": 5, "percentage": 100.0}
    ]


def test_insights_require_authentication(client):
    response = client.get("/insights")
    assert response.status_code == 401
    assert response.json()["detail"] == "ログインが必要です。"
