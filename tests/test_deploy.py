from app import create_app


def test_deploy_rejects_missing_or_wrong_token(monkeypatch):
    monkeypatch.setenv("DEPLOY_SECRET", "right-token")
    client = create_app("testing").test_client()

    assert client.post("/deploy").status_code == 403
    assert client.post("/deploy", headers={"X-Deploy-Token": "wrong"}).status_code == 403