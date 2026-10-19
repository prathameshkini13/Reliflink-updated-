/**
 * Disaster Relief Resource Allocation Platform - Frontend Interactive Logic.
 * Handles Chart.js rendering, AJAX API calls with CSRF tokens, CSV parsing & dropzone.
 */

let allocationChartInstance = null;

document.addEventListener("DOMContentLoaded", () => {
  initSliders();
  initChart();
  initForm();
  initSimulateButton();
  initDropZone();

  // Run initial allocation on page load
  calculateAllocation();
});

function getCsrfToken() {
  const meta = document.querySelector('meta[name="csrf-token"]');
  return meta ? meta.getAttribute("content") : "";
}

function initSliders() {
  const vulnInput = document.getElementById("vulnerability_index");
  const vulnVal = document.getElementById("vuln-val");
  const infraInput = document.getElementById("infrastructure_damage_pct");
  const infraVal = document.getElementById("infra-val");

  vulnInput.addEventListener("input", (e) => {
    vulnVal.textContent = parseFloat(e.target.value).toFixed(2);
  });

  infraInput.addEventListener("input", (e) => {
    infraVal.textContent = `${e.target.value}%`;
  });
}

function initChart() {
  const ctx = document.getElementById("allocationChart");
  if (!ctx) return;

  const labels = ["Water (100L)", "Food (Packs)", "Trauma Kits", "Shelters", "Solar Units"];
  const demandData = [436, 291, 140, 150, 97];
  const allocatedData = [436, 291, 140, 150, 97];

  allocationChartInstance = new Chart(ctx, {
    type: "bar",
    data: {
      labels: labels,
      datasets: [
        {
          label: "Gross Demand",
          data: demandData,
          backgroundColor: "rgba(148, 163, 184, 0.35)",
          borderColor: "#94a3b8",
          borderWidth: 1,
          borderRadius: 4,
        },
        {
          label: "Allocated Supply",
          data: allocatedData,
          backgroundColor: "rgba(37, 99, 235, 0.8)",
          borderColor: "#3b82f6",
          borderWidth: 1,
          borderRadius: 4,
        },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          position: "top",
          labels: { color: "#94a3b8", font: { family: "Plus Jakarta Sans", size: 11 } },
        },
        tooltip: {
          backgroundColor: "#1e293b",
          titleColor: "#f8fafc",
          bodyColor: "#cbd5e1",
          borderColor: "#334155",
          borderWidth: 1,
        },
      },
      scales: {
        x: {
          ticks: { color: "#94a3b8", font: { family: "Plus Jakarta Sans", size: 10 } },
          grid: { display: false },
        },
        y: {
          ticks: { color: "#94a3b8", font: { family: "JetBrains Mono", size: 10 } },
          grid: { color: "#1e293b" },
        },
      },
    },
  });
}

function initForm() {
  const form = document.getElementById("incident-form");
  form.addEventListener("submit", (e) => {
    e.preventDefault();
    calculateAllocation();
  });
}

async function calculateAllocation() {
  const payload = {
    zone_id: document.getElementById("zone_id").value.trim(),
    disaster_type: document.getElementById("disaster_type").value,
    affected_population: parseFloat(document.getElementById("affected_population").value),
    vulnerability_index: parseFloat(document.getElementById("vulnerability_index").value),
    infrastructure_damage_pct: parseFloat(document.getElementById("infrastructure_damage_pct").value),
    urgency_window_hours: parseFloat(document.getElementById("urgency_window_hours").value),
    distance_km: parseFloat(document.getElementById("distance_km").value),
  };

  try {
    const res = await fetch("/api/allocate", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": getCsrfToken(),
      },
      body: JSON.stringify(payload),
    });

    const data = await res.json();
    if (res.ok && data.status === "PROCESSED") {
      updateDashboard(data);
    } else {
      alert(`Allocation Error: ${data.errors ? data.errors.join(", ") : data.error}`);
    }
  } catch (err) {
    console.error("Network or execution error:", err);
  }
}

function updateDashboard(data) {
  // Update Triage badge
  const triageBadge = document.getElementById("triage-badge");
  const priority = data.triage.priority_level;
  const score = data.triage.score;
  triageBadge.textContent = `${priority} (${score})`;
  triageBadge.className = `badge badge-triage badge-${priority.toLowerCase()}`;

  // Update KPIs
  document.getElementById("kpi-zones").textContent = "1 Active";
  document.getElementById("kpi-population").textContent = Number(data.allocation.demands.food_ration_packs / 6).toLocaleString();
  document.getElementById("kpi-sustainability").textContent = `${data.sustainability.sdg11_sustainability_score}%`;
  document.getElementById("kpi-fulfillment").textContent = `${data.allocation.overall_fulfillment_pct}%`;

  // Update Chart
  if (allocationChartInstance) {
    const demands = data.allocation.demands;
    const allocated = data.allocation.allocated;

    // Rescale water by /100 for visual chart harmony
    const demandValues = [
      Math.round(demands.potable_water_liters / 100),
      demands.food_ration_packs,
      demands.medical_kits,
      demands.emergency_shelters,
      demands.solar_power_units,
    ];

    const allocatedValues = [
      Math.round(allocated.potable_water_liters / 100),
      allocated.food_ration_packs,
      allocated.medical_kits,
      allocated.emergency_shelters,
      allocated.solar_power_units,
    ];

    allocationChartInstance.data.datasets[0].data = demandValues;
    allocationChartInstance.data.datasets[1].data = allocatedValues;
    allocationChartInstance.update();
  }

  // Update Sustainability Stats
  document.getElementById("stat-freight").textContent = `${data.sustainability.freight_co2_emissions_kg} kg`;
  document.getElementById("stat-solar-avoided").textContent = `${data.sustainability.solar_co2_avoided_kg} kg CO₂`;
  document.getElementById("stat-eco-pack").textContent = `${data.sustainability.eco_pack_savings_kg} kg CO₂`;
  document.getElementById("stat-net-carbon").textContent = `${data.sustainability.net_co2_impact_kg} kg`;

  // Update Alerts
  const alertsContainer = document.getElementById("alerts-container");
  alertsContainer.innerHTML = "";

  (data.alerts || []).forEach((alert) => {
    const div = document.createElement("div");
    const severityClass = alert.severity === "CRITICAL" ? "alert-critical" : (alert.severity === "WARNING" ? "alert-warning" : "alert-optimal");
    const icon = alert.severity === "CRITICAL" ? "⚠️" : (alert.severity === "WARNING" ? "⚡" : "✅");

    div.className = `alert-item ${severityClass}`;
    div.innerHTML = `
      <div class="alert-icon">${icon}</div>
      <div class="alert-body">
        <strong>${alert.code}</strong>
        <p>${alert.message}</p>
      </div>
    `;
    alertsContainer.appendChild(div);
  });
}

function initSimulateButton() {
  const btn = document.getElementById("btn-simulate");
  btn.addEventListener("click", async () => {
    btn.disabled = true;
    btn.innerHTML = "Simulating...";

    try {
      const res = await fetch("/api/simulate");
      const data = await res.json();
      if (data.scenarios && data.scenarios.length > 0) {
        // Send batch scenarios
        const batchRes = await fetch("/api/batch", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": getCsrfToken(),
          },
          body: JSON.stringify(data.scenarios),
        });

        const batchData = await batchRes.json();
        if (batchData.processed && batchData.processed.length > 0) {
          // Display top priority scenario on dashboard
          updateDashboard(batchData.processed[0]);
          document.getElementById("kpi-zones").textContent = `${batchData.total_processed} Zones`;

          // Populate input form with the highest urgency zone
          const topZone = batchData.processed[0];
          document.getElementById("zone_id").value = topZone.zone_id;
          document.getElementById("disaster_type").value = topZone.disaster_type;
        }
      }
    } catch (e) {
      console.error("Simulation failed:", e);
    } finally {
      btn.disabled = false;
      btn.innerHTML = `
        <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2">
          <polyline points="23 4 23 10 17 10"></polyline>
          <path d="M20.49 15a9 9 0 1 1-2.12-9.36L23 10"></path>
        </svg> Run Multi-Zone Simulation
      `;
    }
  });
}

function initDropZone() {
  const dropZone = document.getElementById("drop-zone");
  const fileInput = document.getElementById("csv-file-input");

  dropZone.addEventListener("click", () => fileInput.click());

  dropZone.addEventListener("dragover", (e) => {
    e.preventDefault();
    dropZone.classList.add("dragover");
  });

  dropZone.addEventListener("dragleave", () => {
    dropZone.classList.remove("dragover");
  });

  dropZone.addEventListener("drop", (e) => {
    e.preventDefault();
    dropZone.classList.remove("dragover");
    if (e.dataTransfer.files.length) {
      handleCsvFile(e.dataTransfer.files[0]);
    }
  });

  fileInput.addEventListener("change", (e) => {
    if (e.target.files.length) {
      handleCsvFile(e.target.files[0]);
    }
  });
}

async function handleCsvFile(file) {
  if (!file.name.endsWith(".csv")) {
    alert("Please upload a valid .csv file.");
    return;
  }

  const formData = new FormData();
  formData.append("file", file);

  try {
    const res = await fetch("/api/batch", {
      method: "POST",
      headers: {
        "X-CSRFToken": getCsrfToken(),
      },
      body: formData,
    });

    const data = await res.json();
    if (res.ok && data.processed && data.processed.length > 0) {
      updateDashboard(data.processed[0]);
      document.getElementById("kpi-zones").textContent = `${data.total_processed} Zones (CSV)`;
      alert(`Successfully processed ${data.total_processed} disaster zones from ${file.name}`);
    } else {
      alert(`Batch Processing Error: ${data.error || "Malformed file"}`);
    }
  } catch (err) {
    console.error("CSV upload error:", err);
  }
}
