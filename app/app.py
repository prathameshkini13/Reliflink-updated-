"""Disaster Relief Resource Allocation Platform - Flask Web Application.

Delivered through a secure DevSecOps pipeline with CSRF protection,
hardened security headers, and strict input validation.
Aligned with Course Outcome CO2 and UN SDG 11.
"""
import os
import secrets
from flask import Flask, jsonify, render_template, request
from flask_wtf.csrf import CSRFError, CSRFProtect, generate_csrf

from core import (
    DEFAULT_WAREHOUSE,
    DatasetError,
    parse_csv,
    process_disaster_batch,
    process_disaster_report,
    simulate_disaster_session,
)

MAX_UPLOAD_BYTES = 2 * 1024 * 1024  # 2 MB payload protection

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = MAX_UPLOAD_BYTES
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY") or secrets.token_hex(32)
app.config["WTF_CSRF_TIME_LIMIT"] = 7200

csrf = CSRFProtect(app)


@app.after_request
def set_security_headers(response):
    """Enforce defense-in-depth HTTP security headers (OWASP guidelines)."""
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
    response.headers["Content-Security-Policy"] = (
        "default-src 'self'; "
        "script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; "
        "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
        "font-src 'self' https://fonts.gstatic.com; "
        "img-src 'self' data:; "
        "frame-ancestors 'none'"
    )
    return response


@app.errorhandler(CSRFError)
def handle_csrf_error(err):
    """Handle CSRF validation failures securely."""
    return jsonify({
        "status": "ERROR",
        "error": "CSRF validation failed",
        "message": str(err.description),
    }), 400


@app.errorhandler(413)
def handle_large_payload(err):
    """Handle payload size violations."""
    return jsonify({
        "status": "ERROR",
        "error": "Payload exceeds 2MB limit",
    }), 413


@app.errorhandler(404)
def handle_not_found(err):
    """Handle route not found."""
    return jsonify({
        "status": "ERROR",
        "error": "Resource not found",
    }), 404


@app.errorhandler(500)
def handle_internal_error(err):
    """Handle uncaught server errors without leaking internals."""
    return jsonify({
        "status": "ERROR",
        "error": "Internal platform error occurred",
    }), 500


@app.get("/")
def index():
    """Render the main interactive platform interface."""
    token = generate_csrf()
    return render_template("index.html", csrf_token=token)


@app.get("/health")
def health():
    """Liveness and readiness probe for container orchestrators and load balancers."""
    return jsonify({
        "status": "healthy",
        "service": "disaster-relief-resource-allocator",
        "version": "1.0.0",
        "sdg_target": "SDG 11 - Sustainable Cities and Communities",
        "course_outcome": "CO2",
    }), 200


@app.get("/api/warehouse")
def get_warehouse():
    """Retrieve current baseline warehouse stockpile levels."""
    return jsonify({
        "status": "SUCCESS",
        "inventory": DEFAULT_WAREHOUSE,
    }), 200


@app.get("/api/sample")
def get_sample_incident():
    """Provide a verified template incident for quick testing and simulation."""
    return jsonify({
        "status": "SUCCESS",
        "sample": {
            "zone_id": "Sector-9 River Delta",
            "disaster_type": "Flash Flood",
            "affected_population": 4850,
            "vulnerability_index": 0.72,
            "infrastructure_damage_pct": 65.0,
            "urgency_window_hours": 18.0,
            "distance_km": 42.5,
        }
    }), 200


@app.get("/api/simulate")
def get_simulation():
    """Return synthetic multi-zone disaster scenario feed."""
    scenarios = simulate_disaster_session(count=5)
    return jsonify({
        "status": "SUCCESS",
        "scenarios": scenarios,
    }), 200


@app.post("/api/allocate")
def allocate_single():
    """API endpoint to triage and allocate supplies for a single disaster incident."""
    if not request.is_json:
        return jsonify({"status": "ERROR", "error": "Request body must be JSON"}), 400

    payload = request.get_json()
    result = process_disaster_report(payload)

    if result.get("status") == "REJECTED":
        return jsonify(result), 422

    return jsonify(result), 200


@app.post("/api/batch")
def allocate_batch():
    """API endpoint to process batch incidents via JSON array or CSV upload."""
    if request.is_json:
        payload = request.get_json()
        if not isinstance(payload, list):
            return jsonify({"status": "ERROR", "error": "Batch payload must be a JSON array"}), 400
        reports = payload
    elif "file" in request.files:
        uploaded_file = request.files["file"]
        if uploaded_file.filename == "":
            return jsonify({"status": "ERROR", "error": "No selected file"}), 400
        try:
            content = uploaded_file.read().decode("utf-8")
            reports = parse_csv(content)
        except (DatasetError, UnicodeDecodeError) as ex:
            return jsonify({"status": "ERROR", "error": str(ex)}), 400
    elif request.data:
        try:
            content = request.data.decode("utf-8")
            reports = parse_csv(content)
        except DatasetError as ex:
            return jsonify({"status": "ERROR", "error": str(ex)}), 400
    else:
        return jsonify({"status": "ERROR", "error": "No batch data provided"}), 400

    batch_result = process_disaster_batch(reports)
    return jsonify(batch_result), 200


if __name__ == "__main__":
    # Local development server
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
