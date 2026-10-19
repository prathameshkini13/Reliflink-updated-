"""Integration tests for Flask application routes, CSRF security, and headers."""
import io
import json


def test_index_route(client):
    res = client.get("/")
    assert res.status_code == 200
    html = res.data.decode("utf-8")
    assert "RELIEF-ALLOC" in html
    assert "Kini Prathamesh Prakash" in html
    assert "124BTCS1057" in html
    assert "CO2" in html
    assert "SDG 11" in html


def test_security_headers(client):
    res = client.get("/health")
    assert res.status_code == 200
    assert res.headers["X-Content-Type-Options"] == "nosniff"
    assert res.headers["X-Frame-Options"] == "DENY"
    assert res.headers["Referrer-Policy"] == "strict-origin-when-cross-origin"
    assert "default-src 'self'" in res.headers["Content-Security-Policy"]
    assert "frame-ancestors 'none'" in res.headers["Content-Security-Policy"]


def test_health_route(client):
    res = client.get("/health")
    assert res.status_code == 200
    data = res.get_json()
    assert data["status"] == "healthy"
    assert data["service"] == "disaster-relief-resource-allocator"
    assert "SDG 11" in data["sdg_target"]
    assert data["course_outcome"] == "CO2"


def test_warehouse_route(client):
    res = client.get("/api/warehouse")
    assert res.status_code == 200
    data = res.get_json()
    assert data["status"] == "SUCCESS"
    assert "potable_water_liters" in data["inventory"]


def test_sample_route(client):
    res = client.get("/api/sample")
    assert res.status_code == 200
    data = res.get_json()
    assert data["status"] == "SUCCESS"
    assert data["sample"]["disaster_type"] == "Flash Flood"


def test_simulate_route(client):
    res = client.get("/api/simulate")
    assert res.status_code == 200
    data = res.get_json()
    assert data["status"] == "SUCCESS"
    assert len(data["scenarios"]) == 5


def test_allocate_single_success(client, valid_incident):
    res = client.post(
        "/api/allocate",
        data=json.dumps(valid_incident),
        content_type="application/json",
    )
    assert res.status_code == 200
    data = res.get_json()
    assert data["status"] == "PROCESSED"
    assert data["allocation"]["overall_fulfillment_pct"] == 100.0


def test_allocate_single_not_json(client):
    res = client.post("/api/allocate", data="not-json", content_type="text/plain")
    assert res.status_code == 400
    data = res.get_json()
    assert "Request body must be JSON" in data["error"]


def test_allocate_single_invalid_data_422(client):
    invalid_data = {"zone_id": "Zone-A", "disaster_type": "InvalidDisaster"}
    res = client.post(
        "/api/allocate",
        data=json.dumps(invalid_data),
        content_type="application/json",
    )
    assert res.status_code == 422
    data = res.get_json()
    assert data["status"] == "REJECTED"
    assert len(data["errors"]) > 0


def test_allocate_batch_json_array(client, valid_incident):
    batch = [valid_incident, valid_incident]
    res = client.post(
        "/api/batch",
        data=json.dumps(batch),
        content_type="application/json",
    )
    assert res.status_code == 200
    data = res.get_json()
    assert data["total_submitted"] == 2
    assert data["total_processed"] == 2


def test_allocate_batch_json_not_array(client):
    res = client.post(
        "/api/batch",
        data=json.dumps({"not": "an array"}),
        content_type="application/json",
    )
    assert res.status_code == 400
    data = res.get_json()
    assert "must be a JSON array" in data["error"]


def test_allocate_batch_csv_upload(client, sample_csv_text):
    data = {
        "file": (io.BytesIO(sample_csv_text.encode("utf-8")), "disasters.csv"),
    }
    res = client.post(
        "/api/batch",
        data=data,
        content_type="multipart/form-data",
    )
    assert res.status_code == 200
    result = res.get_json()
    assert result["total_submitted"] == 2
    assert result["total_processed"] == 2


def test_allocate_batch_csv_raw_data(client, sample_csv_text):
    res = client.post(
        "/api/batch",
        data=sample_csv_text,
        content_type="text/csv",
    )
    assert res.status_code == 200
    result = res.get_json()
    assert result["total_submitted"] == 2


def test_allocate_batch_empty_filename(client):
    data = {
        "file": (io.BytesIO(b""), ""),
    }
    res = client.post(
        "/api/batch",
        data=data,
        content_type="multipart/form-data",
    )
    assert res.status_code == 400
    assert "No selected file" in res.get_json()["error"]


def test_allocate_batch_malformed_csv(client):
    res = client.post(
        "/api/batch",
        data="invalid,csv,content\n1,2,3",
        content_type="text/csv",
    )
    assert res.status_code == 400
    assert "Missing required CSV columns" in res.get_json()["error"]


def test_allocate_batch_missing_payload(client):
    res = client.post("/api/batch")
    assert res.status_code == 400
    assert "No batch data provided" in res.get_json()["error"]


def test_csrf_protection_rejection(csrf_client, valid_incident):
    """Ensure mutating endpoints reject requests without a CSRF token when enabled."""
    res = csrf_client.post(
        "/api/allocate",
        data=json.dumps(valid_incident),
        content_type="application/json",
    )
    assert res.status_code == 400
    data = res.get_json()
    assert data["status"] == "ERROR"
    assert "CSRF validation failed" in data["error"]


def test_404_not_found(client):
    res = client.get("/non-existent-endpoint")
    assert res.status_code == 404
    data = res.get_json()
    assert data["error"] == "Resource not found"
