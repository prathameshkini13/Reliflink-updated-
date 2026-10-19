"""Unit tests for app/core.py (Course Outcome CO2 & SDG 11 Modular Engines)."""
import pytest
from core import (
    DEFAULT_WAREHOUSE,
    DISASTER_PROFILES,
    DatasetError,
    allocate_resources,
    calculate_triage_score,
    evaluate_sustainability,
    generate_dispatch_alert,
    parse_csv,
    process_disaster_batch,
    process_disaster_report,
    simulate_disaster_session,
    validate_disaster_report,
)


def test_validate_disaster_report_success(valid_incident):
    is_valid, errors = validate_disaster_report(valid_incident)
    assert is_valid is True
    assert len(errors) == 0


def test_validate_disaster_report_not_dict():
    is_valid, errors = validate_disaster_report("invalid-payload")
    assert is_valid is False
    assert "must be a dictionary" in errors[0]


def test_validate_disaster_report_empty_zone(valid_incident):
    valid_incident["zone_id"] = "   "
    is_valid, errors = validate_disaster_report(valid_incident)
    assert is_valid is False
    assert any("Zone ID is required" in e for e in errors)


def test_validate_disaster_report_invalid_disaster_type(valid_incident):
    valid_incident["disaster_type"] = "MeteorStrike"
    is_valid, errors = validate_disaster_report(valid_incident)
    assert is_valid is False
    assert any("Invalid disaster type" in e for e in errors)


def test_validate_disaster_report_population_bounds(valid_incident):
    # Non-numeric
    valid_incident["affected_population"] = "many"
    is_valid, errors = validate_disaster_report(valid_incident)
    assert is_valid is False

    # Negative
    valid_incident["affected_population"] = -5
    is_valid, errors = validate_disaster_report(valid_incident)
    assert is_valid is False

    # Exceeding 5M
    valid_incident["affected_population"] = 6000000
    is_valid, errors = validate_disaster_report(valid_incident)
    assert is_valid is False


def test_validate_disaster_report_vulnerability_bounds(valid_incident):
    valid_incident["vulnerability_index"] = 1.45
    is_valid, errors = validate_disaster_report(valid_incident)
    assert is_valid is False
    assert any("Vulnerability index must be between" in e for e in errors)

    valid_incident["vulnerability_index"] = "high"
    is_valid, errors = validate_disaster_report(valid_incident)
    assert is_valid is False


def test_validate_disaster_report_infrastructure_bounds(valid_incident):
    valid_incident["infrastructure_damage_pct"] = -10
    is_valid, errors = validate_disaster_report(valid_incident)
    assert is_valid is False

    valid_incident["infrastructure_damage_pct"] = 105
    is_valid, errors = validate_disaster_report(valid_incident)
    assert is_valid is False

    valid_incident["infrastructure_damage_pct"] = "shattered"
    is_valid, errors = validate_disaster_report(valid_incident)
    assert is_valid is False


def test_validate_disaster_report_urgency_bounds(valid_incident):
    valid_incident["urgency_window_hours"] = 0
    is_valid, errors = validate_disaster_report(valid_incident)
    assert is_valid is False

    valid_incident["urgency_window_hours"] = 999
    is_valid, errors = validate_disaster_report(valid_incident)
    assert is_valid is False

    valid_incident["urgency_window_hours"] = "soon"
    is_valid, errors = validate_disaster_report(valid_incident)
    assert is_valid is False


def test_validate_disaster_report_distance_bounds(valid_incident):
    valid_incident["distance_km"] = -1
    is_valid, errors = validate_disaster_report(valid_incident)
    assert is_valid is False

    valid_incident["distance_km"] = 25000
    is_valid, errors = validate_disaster_report(valid_incident)
    assert is_valid is False

    valid_incident["distance_km"] = "far"
    is_valid, errors = validate_disaster_report(valid_incident)
    assert is_valid is False


def test_calculate_triage_score_critical(valid_incident):
    valid_incident.update({
        "disaster_type": "Tsunami",
        "affected_population": 50000,
        "vulnerability_index": 0.95,
        "infrastructure_damage_pct": 90.0,
        "urgency_window_hours": 6.0,
    })
    triage = calculate_triage_score(valid_incident)
    assert triage["priority_level"] == "CRITICAL"
    assert triage["score"] >= 75.0
    assert triage["urgency_factor"] > 1.0


def test_calculate_triage_score_priority_tiers():
    # Low priority
    low_incident = {
        "disaster_type": "Landslide",
        "affected_population": 50,
        "vulnerability_index": 0.05,
        "infrastructure_damage_pct": 5.0,
        "urgency_window_hours": 200.0,
    }
    triage_low = calculate_triage_score(low_incident)
    assert triage_low["priority_level"] in ("LOW", "MEDIUM")

    # High priority
    high_incident = {
        "disaster_type": "Flash Flood",
        "affected_population": 8000,
        "vulnerability_index": 0.5,
        "infrastructure_damage_pct": 50.0,
        "urgency_window_hours": 24.0,
    }
    triage_high = calculate_triage_score(high_incident)
    assert triage_high["priority_level"] in ("HIGH", "CRITICAL")


def test_allocate_resources_standard(valid_incident):
    result = allocate_resources(valid_incident)
    assert "demands" in result
    assert "allocated" in result
    assert result["overall_fulfillment_pct"] == 100.0
    assert result["allocated"]["potable_water_liters"] > 0
    assert result["allocated"]["food_ration_packs"] > 0
    assert result["allocated"]["medical_kits"] > 0
    assert result["allocated"]["emergency_shelters"] > 0
    assert result["allocated"]["solar_power_units"] > 0


def test_allocate_resources_depleted_stock(valid_incident):
    limited_warehouse = {
        "potable_water_liters": 100,
        "food_ration_packs": 50,
        "medical_kits": 5,
        "emergency_shelters": 2,
        "solar_power_units": 1,
    }
    result = allocate_resources(valid_incident, warehouse_stock=limited_warehouse)
    assert result["overall_fulfillment_pct"] < 50.0
    assert result["allocated"]["potable_water_liters"] == 100


def test_evaluate_sustainability_sdg11(valid_incident):
    allocation = allocate_resources(valid_incident)
    sus = evaluate_sustainability(valid_incident, allocation["allocated"])

    assert sus["freight_co2_emissions_kg"] > 0
    assert sus["solar_co2_avoided_kg"] > 0
    assert sus["eco_pack_savings_kg"] > 0
    assert 0 <= sus["sdg11_sustainability_score"] <= 100
    assert sus["circular_packaging_pct"] > 80.0


def test_generate_dispatch_alert_critical(valid_incident):
    triage = {"priority_level": "CRITICAL", "score": 90.0}
    allocation = {
        "overall_fulfillment_pct": 50.0,
        "fulfillment_ratios": {"potable_water_liters": 40.0, "medical_kits": 90.0},
    }
    valid_incident["urgency_window_hours"] = 8.0
    alerts = generate_dispatch_alert(valid_incident, triage, allocation)

    severities = [a["severity"] for a in alerts]
    assert "CRITICAL" in severities
    assert any(a["code"] == "URGENT_SURVIVAL_WINDOW" for a in alerts)
    assert any(a["code"] == "SEVERE_DEFICIT" for a in alerts)
    assert any(a["code"] == "RESOURCE_BOTTLENECK" for a in alerts)


def test_generate_dispatch_alert_optimal(valid_incident):
    triage = {"priority_level": "LOW", "score": 25.0}
    allocation = {
        "overall_fulfillment_pct": 100.0,
        "fulfillment_ratios": {"potable_water_liters": 100.0, "food_ration_packs": 100.0},
    }
    valid_incident["urgency_window_hours"] = 48.0
    alerts = generate_dispatch_alert(valid_incident, triage, allocation)
    assert len(alerts) == 1
    assert alerts[0]["severity"] == "OPTIMAL"
    assert alerts[0]["code"] == "DISPATCH_AUTHORIZED"


def test_generate_dispatch_alert_moderate_shortage(valid_incident):
    triage = {"priority_level": "MEDIUM", "score": 40.0}
    allocation = {
        "overall_fulfillment_pct": 75.0,
        "fulfillment_ratios": {"potable_water_liters": 75.0},
    }
    alerts = generate_dispatch_alert(valid_incident, triage, allocation)
    assert any(a["code"] == "MODERATE_SHORTAGE" for a in alerts)


def test_process_disaster_report_success(valid_incident):
    res = process_disaster_report(valid_incident)
    assert res["status"] == "PROCESSED"
    assert res["zone_id"] == valid_incident["zone_id"]
    assert "triage" in res
    assert "allocation" in res
    assert "sustainability" in res
    assert "alerts" in res
    assert "remaining_warehouse_stock" in res


def test_process_disaster_report_rejected():
    res = process_disaster_report({"invalid": True})
    assert res["status"] == "REJECTED"
    assert len(res["errors"]) > 0


def test_process_disaster_batch(valid_incident):
    second_incident = dict(valid_incident)
    second_incident["zone_id"] = "Zone-Beta"
    second_incident["disaster_type"] = "Earthquake"
    second_incident["urgency_window_hours"] = 6.0

    batch = [valid_incident, second_incident, {"invalid_zone": 1}]
    res = process_disaster_batch(batch)

    assert res["total_submitted"] == 3
    assert res["total_processed"] == 2
    assert res["total_rejected"] == 1
    assert len(res["processed"]) == 2
    # Verify sorting by urgency/triage score
    assert res["processed"][0]["triage"]["score"] >= res["processed"][1]["triage"]["score"]


def test_parse_csv_success(sample_csv_text):
    reports = parse_csv(sample_csv_text)
    assert len(reports) == 2
    assert reports[0]["zone_id"] == "Zone-1"
    assert reports[0]["disaster_type"] == "Earthquake"
    assert reports[1]["zone_id"] == "Zone-2"


def test_parse_csv_empty():
    with pytest.raises(DatasetError, match="empty"):
        parse_csv("")
    with pytest.raises(DatasetError, match="empty"):
        parse_csv("   \n\n  ")


def test_parse_csv_missing_columns():
    csv_missing = "zone_id,disaster_type\nZone-1,Flood\n"
    with pytest.raises(DatasetError, match="Missing required CSV columns"):
        parse_csv(csv_missing)


def test_parse_csv_malformed_number():
    csv_malformed = (
        "zone_id,disaster_type,affected_population,vulnerability_index,"
        "infrastructure_damage_pct,urgency_window_hours,distance_km\n"
        "Zone-1,Earthquake,NOT_A_NUMBER,0.8,70.0,12.0,25.0\n"
    )
    with pytest.raises(DatasetError, match="Malformed numerical data"):
        parse_csv(csv_malformed)


def test_parse_csv_row_limit():
    from core import MAX_BATCH_ROWS
    header = (
        "zone_id,disaster_type,affected_population,vulnerability_index,"
        "infrastructure_damage_pct,urgency_window_hours,distance_km\n"
    )
    rows = "\n".join(["Z,Flash Flood,100,0.5,50,24,10"] * (MAX_BATCH_ROWS + 1))
    with pytest.raises(DatasetError, match="exceeds maximum allowed rows"):
        parse_csv(header + rows)


def test_parse_csv_no_data_rows():
    header = (
        "zone_id,disaster_type,affected_population,vulnerability_index,"
        "infrastructure_damage_pct,urgency_window_hours,distance_km\n"
    )
    with pytest.raises(DatasetError, match="contains no valid data rows"):
        parse_csv(header)


def test_simulate_disaster_session():
    scenarios = simulate_disaster_session(count=4)
    assert len(scenarios) == 4
    for sc in scenarios:
        is_valid, errors = validate_disaster_report(sc)
        assert is_valid is True, f"Generated scenario invalid: {errors}"
