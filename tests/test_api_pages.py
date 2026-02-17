"""
Test page routes return 200 OK.
"""


def test_dashboard_page(client):
    response = client.get("/")
    assert response.status_code == 200


def test_proposals_page(client):
    response = client.get("/proposals")
    assert response.status_code == 200


def test_leads_page(client):
    response = client.get("/leads")
    assert response.status_code == 200


def test_campaigns_page(client):
    response = client.get("/campaigns")
    assert response.status_code == 200


def test_landing_pages_page(client):
    response = client.get("/landing-pages")
    assert response.status_code == 200


def test_assets_page(client):
    response = client.get("/assets")
    assert response.status_code == 200


def test_agents_page(client):
    response = client.get("/agents")
    assert response.status_code == 200


def test_strategy_page(client):
    response = client.get("/strategy")
    assert response.status_code == 200


def test_integrations_page(client):
    response = client.get("/integrations")
    assert response.status_code == 200


def test_api_docs_page(client):
    response = client.get("/api/docs")
    assert response.status_code == 200
    assert b"swagger" in response.data.lower()
