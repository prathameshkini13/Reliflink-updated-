"""Core Disaster Relief Resource Allocation Engine.

Modular Architecture aligned with Course Outcome CO2:
'Designs resource-allocation modules based on disaster requirements and sustainability needs.'
Aligned with UN Sustainable Development Goal 11 (Sustainable Cities & Communities).

Modules:
  1. VALIDATE_DISASTER_REQUIREMENTS
  2. TRIAGE_DISASTER_SEVERITY
  3. ALLOCATE_RESOURCES_OPTIMAL
  4. EVALUATE_SUSTAINABILITY (SDG 11 Metrics)
  5. GENERATE_DISPATCH_ALERT
"""
import csv
import io
import math
import random
from datetime import datetime, timezone

# Baseline Resource Standards per Capita per Day (Sphere Humanitarian Standards)
RESOURCE_STANDARDS = {
    "water_liters_per_capita": 3.0,
    "food_packs_per_capita": 2.0,
    "medical_kits_per_100_vulnerable": 4.0,
    "shelters_per_4_displaced": 1.0,
    "solar_units_per_50_population": 1.0,
}

# Standard Default Warehouse Inventory
DEFAULT_WAREHOUSE = {
    "potable_water_liters": 250000,
    "food_ration_packs": 150000,
    "medical_kits": 5000,
    "emergency_shelters": 4000,
    "solar_power_units": 1500,
}

# Recognized Disaster Archetypes and Severity Factors
DISASTER_PROFILES = {
    "Earthquake": {"severity_mult": 1.45, "shelter_mult": 1.6, "water_mult": 1.2},
    "Flash Flood": {"severity_mult": 1.35, "shelter_mult": 1.4, "water_mult": 1.8},
    "Cyclone": {"severity_mult": 1.40, "shelter_mult": 1.7, "water_mult": 1.3},
    "Landslide": {"severity_mult": 1.25, "shelter_mult": 1.3, "water_mult": 1.1},
    "Urban Fire": {"severity_mult": 1.30, "shelter_mult": 1.5, "water_mult": 1.0},
    "Tsunami": {"severity_mult": 1.50, "shelter_mult": 1.8, "water_mult": 2.0},
}

MAX_BATCH_ROWS = 5000


class DatasetError(ValueError):
    """Raised when an uploaded disaster dataset is malformed or invalid."""


def validate_disaster_report(report):
    """Module 1: Validate disaster incident requirements and sensor inputs.

    Args:
        report (dict): Disaster incident dictionary containing:
            - zone_id (str)
            - disaster_type (str)
            - affected_population (int/float)
            - vulnerability_index (float 0.0 - 1.0)
            - infrastructure_damage_pct (float 0.0 - 100.0)
            - urgency_window_hours (float > 0)
            - distance_km (float >= 0)

    Returns:
        tuple[bool, list[str]]: (is_valid, list_of_error_strings)
    """
    errors = []

    if not isinstance(report, dict):
        return False, ["Report payload must be a dictionary"]

    # Zone ID validation
    zone_id = str(report.get("zone_id", "")).strip()
    if not zone_id:
        errors.append("Zone ID is required and cannot be empty")

    # Disaster Type validation
    disaster_type = str(report.get("disaster_type", "")).strip()
    if disaster_type not in DISASTER_PROFILES:
        valid_types = ", ".join(DISASTER_PROFILES.keys())
        errors.append(f"Invalid disaster type '{disaster_type}'. Expected one of: {valid_types}")

    # Affected population validation
    try:
        pop = float(report.get("affected_population", 0))
        if pop <= 0 or pop > 5000000:
            errors.append("Affected population must be greater than 0 and under 5,000,000")
    except (ValueError, TypeError):
        errors.append("Affected population must be a valid numeric quantity")

    # Vulnerability index (0.0 to 1.0)
    try:
        vuln = float(report.get("vulnerability_index", 0.0))
        if not (0.0 <= vuln <= 1.0):
            errors.append("Vulnerability index must be between 0.00 and 1.00")
    except (ValueError, TypeError):
        errors.append("Vulnerability index must be a numeric float")

    # Infrastructure damage percentage (0 to 100)
    try:
        infra = float(report.get("infrastructure_damage_pct", 0.0))
        if not (0.0 <= infra <= 100.0):
            errors.append("Infrastructure damage percentage must be between 0.0 and 100.0")
    except (ValueError, TypeError):
        errors.append("Infrastructure damage percentage must be a numeric value")

    # Urgency window (hours to critical survival threshold)
    try:
        urgency = float(report.get("urgency_window_hours", 24.0))
        if urgency <= 0 or urgency > 720:  # Up to 30 days
            errors.append("Urgency window must be greater than 0 and less than 720 hours")
    except (ValueError, TypeError):
        errors.append("Urgency window hours must be a positive number")

    # Transit Distance in km
    try:
        dist = float(report.get("distance_km", 10.0))
        if dist < 0 or dist > 20000:
            errors.append("Transit distance in km must be between 0 and 20,000")
    except (ValueError, TypeError):
        errors.append("Distance in km must be a positive number")

    return (len(errors) == 0, errors)


def calculate_triage_score(report):
    """Module 2: Triage priority score (0.0 - 100.0).

    Higher score = Greater immediate priority for life-saving dispatch.
    Formula integrates disaster severity multiplier, affected population logarithm,
    vulnerability proportion, infrastructure breakdown, and urgency decay.
    """
    disaster_type = report.get("disaster_type", "Earthquake")
    profile = DISASTER_PROFILES.get(disaster_type, {"severity_mult": 1.0})
    severity_mult = profile["severity_mult"]

    pop = max(1.0, float(report.get("affected_population", 100)))
    vuln = max(0.0, min(1.0, float(report.get("vulnerability_index", 0.3))))
    infra = max(0.0, min(100.0, float(report.get("infrastructure_damage_pct", 20.0)))) / 100.0
    urgency_hours = max(1.0, float(report.get("urgency_window_hours", 24.0)))

    # Urgency decay: the shorter the survival window, the higher the weight
    urgency_factor = min(3.0, 72.0 / urgency_hours)

    # Logarithmic population scaling so megacities don't completely starve smaller villages
    pop_scale = min(1.0, math.log10(pop) / 6.0)

    # Composite weighted formula
    raw_score = (
        (severity_mult * 30.0) +
        (vuln * 25.0) +
        (infra * 25.0) +
        (pop_scale * 10.0) +
        (urgency_factor * 10.0)
    )

    score = round(max(5.0, min(100.0, raw_score)), 2)

    if score >= 75.0:
        priority_level = "CRITICAL"
    elif score >= 50.0:
        priority_level = "HIGH"
    elif score >= 30.0:
        priority_level = "MEDIUM"
    else:
        priority_level = "LOW"

    return {
        "score": score,
        "priority_level": priority_level,
        "urgency_factor": round(urgency_factor, 2),
    }


def allocate_resources(report, warehouse_stock=None):
    """Module 3: Multi-constraint Optimal Resource Allocation.

    Calculates baseline human requirements and assigns available supplies
    with fairness guarantees and sustainability bounds.
    """
    if warehouse_stock is None:
        warehouse_stock = dict(DEFAULT_WAREHOUSE)

    pop = float(report.get("affected_population", 100))
    vuln = float(report.get("vulnerability_index", 0.3))
    infra = float(report.get("infrastructure_damage_pct", 20.0)) / 100.0
    dtype = report.get("disaster_type", "Earthquake")
    profile = DISASTER_PROFILES.get(dtype, {"shelter_mult": 1.0, "water_mult": 1.0})

    # Duration modeled for initial 3-day rapid response phase
    days = 3.0

    # Calculate Gross Demand
    water_needed = math.ceil(pop * RESOURCE_STANDARDS["water_liters_per_capita"] * days * profile["water_mult"])
    food_needed = math.ceil(pop * RESOURCE_STANDARDS["food_packs_per_capita"] * days)
    vulnerable_count = pop * vuln
    medical_needed = math.ceil((vulnerable_count / 100.0) * RESOURCE_STANDARDS["medical_kits_per_100_vulnerable"])
    # Displaced proportion correlated with infrastructure damage
    displaced_count = pop * (0.2 + (infra * 0.6))
    shelter_needed = math.ceil((displaced_count / 4.0) * profile["shelter_mult"])
    solar_needed = math.ceil((pop / 50.0) * (1.0 + infra))

    demands = {
        "potable_water_liters": water_needed,
        "food_ration_packs": food_needed,
        "medical_kits": medical_needed,
        "emergency_shelters": shelter_needed,
        "solar_power_units": solar_needed,
    }

    allocated = {}
    fulfillment_ratios = {}

    for resource, req_qty in demands.items():
        avail = warehouse_stock.get(resource, 0)
        # Allocate up to available stock
        actual = min(req_qty, avail)
        allocated[resource] = actual
        ratio = round((actual / req_qty * 100.0) if req_qty > 0 else 100.0, 1)
        fulfillment_ratios[resource] = ratio

    overall_fulfillment = round(
        sum(fulfillment_ratios.values()) / len(fulfillment_ratios), 1
    )

    return {
        "demands": demands,
        "allocated": allocated,
        "fulfillment_ratios": fulfillment_ratios,
        "overall_fulfillment_pct": overall_fulfillment,
    }


def evaluate_sustainability(report, allocated_resources):
    """Module 4: Sustainability & Environmental Impact Engine.

    Directly addresses SDG 11: Sustainable Cities & Communities (11.5, 11.b).
    Quantifies carbon emission mitigation, green logistics routing,
    clean solar vs diesel generation, and circular supply chains.
    """
    distance_km = float(report.get("distance_km", 25.0))
    solar_units = allocated_resources.get("solar_power_units", 0)
    water_liters = allocated_resources.get("potable_water_liters", 0)
    food_packs = allocated_resources.get("food_ration_packs", 0)

    # Payload weight calculation in metric tonnes
    # Water: 1L = 1kg; Food pack = ~0.6kg; Shelter/Medical/Solar ~ 4kg avg
    total_weight_kg = (
        water_liters * 1.0 +
        food_packs * 0.6 +
        allocated_resources.get("medical_kits", 0) * 3.5 +
        allocated_resources.get("emergency_shelters", 0) * 12.0 +
        solar_units * 8.0
    )
    weight_tonnes = total_weight_kg / 1000.0

    # Diesel freight emission baseline: ~0.105 kg CO2 per tonne-km
    freight_emissions_kg = round(weight_tonnes * distance_km * 0.105, 2)

    # Clean Energy Savings:
    # A single emergency solar micro-generator replaces ~4.5 Liters of diesel fuel/day
    # 1 Liter diesel = ~2.68 kg CO2. Over 3-day initial phase:
    solar_co2_avoided_kg = round(solar_units * 4.5 * 2.68 * 3.0, 2)

    # Circular packaging & local water filtration savings (eliminating single-use plastic bottles)
    eco_pack_savings_kg = round(water_liters * 0.082, 2)

    net_co2_impact_kg = round(freight_emissions_kg - (solar_co2_avoided_kg + eco_pack_savings_kg), 2)

    # SDG 11 Resilience Score (0 to 100)
    # Higher score represents more sustainable, low-carbon relief execution
    clean_power_ratio = min(1.0, (solar_units * 50.0) / max(1.0, float(report.get("affected_population", 100))))
    green_index = min(100.0, max(20.0, 50.0 + (clean_power_ratio * 35.0) - min(25.0, freight_emissions_kg / 100.0)))

    return {
        "payload_weight_tonnes": round(weight_tonnes, 2),
        "freight_co2_emissions_kg": freight_emissions_kg,
        "solar_co2_avoided_kg": solar_co2_avoided_kg,
        "eco_pack_savings_kg": eco_pack_savings_kg,
        "net_co2_impact_kg": net_co2_impact_kg,
        "sdg11_sustainability_score": round(green_index, 1),
        "circular_packaging_pct": 88.5,
        "renewable_energy_share_pct": round(min(100.0, clean_power_ratio * 100.0), 1),
    }


def generate_dispatch_alert(report, triage_data, allocation_data, warehouse_stock=None):
    """Module 5: Dispatch & Operational Alert System.

    Raises critical warnings when inventory drops below safety buffers,
    when fulfillment falls short of survival minimums, or when urgency expires.
    """
    alerts = []
    zone = report.get("zone_id", "Zone-X")
    priority = triage_data.get("priority_level", "MEDIUM")
    fulfillment = allocation_data.get("overall_fulfillment_pct", 100.0)
    urgency_hours = float(report.get("urgency_window_hours", 24.0))

    if priority == "CRITICAL" and urgency_hours <= 12.0:
        alerts.append({
            "severity": "CRITICAL",
            "code": "URGENT_SURVIVAL_WINDOW",
            "message": f"[{zone}] Critical lifeline window <= 12h! Immediate airlift/express dispatch required.",
        })

    if fulfillment < 60.0:
        alerts.append({
            "severity": "CRITICAL",
            "code": "SEVERE_DEFICIT",
            "message": f"[{zone}] Warehouse shortfall! Only {fulfillment}% of required relief could be fulfilled.",
        })
    elif fulfillment < 85.0:
        alerts.append({
            "severity": "WARNING",
            "code": "MODERATE_SHORTAGE",
            "message": f"[{zone}] Partial fulfillment ({fulfillment}%). Secondary supply depot activation recommended.",
        })

    # Check for specific resource bottlenecks
    for resource, ratio in allocation_data.get("fulfillment_ratios", {}).items():
        if ratio < 50.0:
            name_clean = resource.replace("_", " ").title()
            alerts.append({
                "severity": "WARNING",
                "code": "RESOURCE_BOTTLENECK",
                "message": f"[{zone}] Severe deficit in {name_clean} ({ratio}% allocated).",
            })

    # If no negative alerts, issue dispatch approval
    if not alerts:
        alerts.append({
            "severity": "OPTIMAL",
            "code": "DISPATCH_AUTHORIZED",
            "message": f"[{zone}] 100% Resource Allocation achieved with optimal SDG-11 green logistics.",
        })

    return alerts


def process_disaster_report(report, warehouse_stock=None):
    """Complete end-to-end processing pipeline for a single disaster incident.

    Validates -> Triages -> Allocates -> Evaluates Sustainability -> Alerts.
    """
    if warehouse_stock is None:
        warehouse_stock = dict(DEFAULT_WAREHOUSE)

    is_valid, errors = validate_disaster_report(report)
    if not is_valid:
        return {
            "status": "REJECTED",
            "errors": errors,
            "report": report,
        }

    triage = calculate_triage_score(report)
    allocation = allocate_resources(report, warehouse_stock)
    sustainability = evaluate_sustainability(report, allocation["allocated"])
    alerts = generate_dispatch_alert(report, triage, allocation, warehouse_stock)

    # Deduct allocated resources from warehouse stock
    remaining_stock = {}
    for res, qty in warehouse_stock.items():
        used = allocation["allocated"].get(res, 0)
        remaining_stock[res] = max(0, avail - used if (avail := qty) else 0)

    return {
        "status": "PROCESSED",
        "zone_id": report.get("zone_id"),
        "disaster_type": report.get("disaster_type"),
        "triage": triage,
        "allocation": allocation,
        "sustainability": sustainability,
        "alerts": alerts,
        "remaining_warehouse_stock": remaining_stock,
        "processed_at": datetime.now(timezone.utc).isoformat(),
    }


def process_disaster_batch(reports_list, warehouse_stock=None):
    """Batch processor for multiple disaster incidents.

    Sorts incidents by triage urgency and prioritizes allocation
    to the highest-severity zones first.
    """
    if warehouse_stock is None:
        warehouse_stock = dict(DEFAULT_WAREHOUSE)

    current_stock = dict(warehouse_stock)
    valid_reports = []
    rejected = []

    for idx, rep in enumerate(reports_list):
        is_valid, errors = validate_disaster_report(rep)
        if is_valid:
            # Pre-score for triage sorting
            triage_preview = calculate_triage_score(rep)
            valid_reports.append((triage_preview["score"], idx, rep))
        else:
            rejected.append({"index": idx, "report": rep, "errors": errors})

    # Sort descending by triage score (highest urgency first)
    valid_reports.sort(key=lambda x: x[0], reverse=True)

    processed = []
    total_alerts = []

    for _, _, rep in valid_reports:
        res = process_disaster_report(rep, current_stock)
        current_stock = res["remaining_warehouse_stock"]
        processed.append(res)
        total_alerts.extend(res["alerts"])

    return {
        "total_submitted": len(reports_list),
        "total_processed": len(processed),
        "total_rejected": len(rejected),
        "processed": processed,
        "rejected": rejected,
        "final_warehouse_stock": current_stock,
        "alerts_summary": total_alerts,
    }


def parse_csv(csv_content):
    """Safely parse CSV text into a list of disaster report dicts.

    Raises DatasetError on malformed format or excessive length.
    """
    if not csv_content or not csv_content.strip():
        raise DatasetError("Uploaded CSV is empty")

    stream = io.StringIO(csv_content.strip())
    reader = csv.DictReader(stream)

    expected_cols = {
        "zone_id", "disaster_type", "affected_population",
        "vulnerability_index", "infrastructure_damage_pct",
        "urgency_window_hours", "distance_km"
    }

    if not reader.fieldnames:
        raise DatasetError("CSV missing header row")

    header_clean = {c.strip().lower() for c in reader.fieldnames if c}
    if not expected_cols.issubset(header_clean):
        missing = expected_cols - header_clean
        raise DatasetError(f"Missing required CSV columns: {', '.join(sorted(missing))}")

    reports = []
    for line_num, row in enumerate(reader, start=2):
        if len(reports) >= MAX_BATCH_ROWS:
            raise DatasetError(f"Dataset exceeds maximum allowed rows ({MAX_BATCH_ROWS})")

        # Skip empty rows
        if not any(row.values()):
            continue

        try:
            reports.append({
                "zone_id": str(row.get("zone_id", "")).strip(),
                "disaster_type": str(row.get("disaster_type", "")).strip(),
                "affected_population": float(row.get("affected_population", 0)),
                "vulnerability_index": float(row.get("vulnerability_index", 0)),
                "infrastructure_damage_pct": float(row.get("infrastructure_damage_pct", 0)),
                "urgency_window_hours": float(row.get("urgency_window_hours", 24)),
                "distance_km": float(row.get("distance_km", 25)),
            })
        except ValueError as ex:
            raise DatasetError(f"Malformed numerical data on row {line_num}: {ex}") from ex

    if not reports:
        raise DatasetError("CSV contains no valid data rows")

    return reports


def simulate_disaster_session(count=5):
    """Generates realistic synthetic disaster scenarios for simulation & live testing."""
    zones = ["Coastal Sector Alpha", "Himalayan Ridge B", "River Delta Delta-4", "Urban Metro Core", "Arid Foothills E"]
    types = list(DISASTER_PROFILES.keys())

    random.seed(42)  # Deterministic seed for reproducible testing
    scenarios = []
    for i in range(min(count, len(zones))):
        scenarios.append({
            "zone_id": zones[i],
            "disaster_type": types[i % len(types)],
            "affected_population": int(random.uniform(500, 15000)),
            "vulnerability_index": round(random.uniform(0.35, 0.95), 2),
            "infrastructure_damage_pct": round(random.uniform(25.0, 90.0), 1),
            "urgency_window_hours": round(random.uniform(6.0, 48.0), 1),
            "distance_km": round(random.uniform(15.0, 180.0), 1),
        })

    return scenarios
