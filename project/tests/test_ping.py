def test_ping(test_app) -> None:
    """
    Test the /ping path operation.
    """
    response = test_app.get("/ping")
    assert response.status_code == 200
    assert response.json() == {"environment": "dev", "ping": "pong!", "testing": True}
