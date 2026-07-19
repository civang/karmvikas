import yaml


class TestOpsEndpoints:
    def test_health_returns_ok(self, client):
        res = client.get("/health")
        assert res.status_code == 200
        assert res.get_json()["status"] == "ok"

    def test_ready_checks_database(self, client):
        res = client.get("/ready")
        assert res.status_code == 200
        assert res.get_json()["status"] == "ready"


class TestApiDocs:
    def test_docs_page_renders(self, client):
        res = client.get("/api/docs")
        assert res.status_code == 200
        assert b"swagger-ui" in res.data

    def test_openapi_spec_is_served_and_valid(self, client):
        res = client.get("/static/openapi.yaml")
        assert res.status_code == 200
        spec = yaml.safe_load(res.data)
        assert spec["openapi"].startswith("3.")
        assert spec["info"]["title"] == "Karmvikas HR — REST API"
        # Spot-check that a representative path from each major resource is documented.
        for path in [
            "/auth/login",
            "/employees",
            "/leaves/{leave_id}/approve",
            "/documents/{document_id}/download",
            "/audit-logs",
        ]:
            assert path in spec["paths"], f"missing documented path: {path}"

    def test_every_documented_operation_declares_responses(self, client):
        res = client.get("/static/openapi.yaml")
        spec = yaml.safe_load(res.data)
        methods = ("get", "post", "patch", "put", "delete")
        for path, item in spec["paths"].items():
            for method in methods:
                if method in item:
                    assert "responses" in item[method], f"{method.upper()} {path} has no responses"
