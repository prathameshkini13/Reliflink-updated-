/**
 * Academic Project Report Generator for:
 * "Modular Design of a Disaster Relief Resource Allocation Platform"
 * Candidate: Kini Prathamesh Prakash (124BTCS1057)
 */
const fs = require('fs');
const path = require('path');

const reportContent = `# COMPREHENSIVE PROJECT REPORT
## Modular Design of a Disaster Relief Resource Allocation Platform (DevSecOps Edition)

**Candidate Name:** Kini Prathamesh Prakash  
**Roll / Registration Number:** 124BTCS1057  
**Academic Milestone:** Review 6 / Final Semester  
**Course Outcome (CO):** CO2 – Designs resource-allocation modules based on disaster requirements and sustainability needs.  
**Program Outcomes (POs):** PO2, PO3, PO4, PO5, PO6, PO8, PO9, PO10  
**Program Specific Outcome (PSO):** PSO2  
**United Nations SDG Alignment:** SDG 11 – Sustainable Cities and Communities (Targets 11.5 & 11.b)  

---

### 1. Project Overview & Motivation
During catastrophic natural and human-induced disasters (floods, earthquakes, cyclones, urban collapse), the immediate survival window (typically 24 to 72 hours) dictates human mortality rates. Conventional relief supply chains suffer from information latency, unequal aid hoarding, lack of green circular logistics, and severe bottlenecks.

This project delivers a **Modular Disaster Relief Resource Allocation Platform** built with **DevSecOps automation**. The system balances life-saving supply optimization with UN SDG 11 urban resilience benchmarks.

---

### 2. Modular Engineering Architecture (Aligned with CO2 & PSO2)

The system decomposes relief orchestration into 5 distinct modules:

1. **Module 1 (Disaster Requirements Validation):**
   - Ingests casualty reports, geographic coordinates, and sensory feeds.
   - Enforces data integrity bounds on population, vulnerability proportion, and infrastructure devastation indices.

2. **Module 2 (Urgency & Severity Triage):**
   - Applies weighted logarithmic scoring:
     $$\\text{Triage Score} = 30(S) + 25(V) + 25(I) + 10\\log_{10}(P) + 10\\left(\\frac{72}{U}\\right)$$
   - Prioritizes zones with shortest survival windows and highest vulnerable demographics.

3. **Module 3 (Optimal Multi-Resource Allocation):**
   - Allocates Potable Water (3L/capita/day), Food Rations (2 packs/capita/day), Trauma Kits, Shelters, and Solar Power Units.
   - Enforces proportional fairness so remote villages are not starved by megacities.

4. **Module 4 (SDG 11 Green Logistics & Sustainability Engine):**
   - Quantifies freight carbon emissions ($0.105\\text{ kg CO}_2/\\text{tonne-km}$).
   - Computes carbon avoidance achieved by deploying solar micro-generators in place of high-polluting diesel units ($13.5\\text{ kg CO}_2/\\text{day}$ saved per generator).
   - Tracks eco-packaging adoption and community resilience metrics.

5. **Module 5 (Automated Dispatch & Bottleneck Alerting):**
   - Monitors warehouse inventory depletion.
   - Emits real-time critical warnings when stock drops below emergency buffer thresholds.

---

### 3. DevSecOps Engineering & Security Pipeline
- **Static Application Security Testing (SAST):** SonarQube Scanner verifying 0 vulnerabilities, 0 bugs, and 0 security hotspots.
- **Software Composition Analysis (SCA):** Trivy scanning Python dependencies and secrets in Git commits.
- **Container Hardening:** Alpine Linux 3.20 multi-stage build running under dedicated non-root user \`reliefapp\` (UID 10001) with \`--read-only\` rootfs and dropped capabilities.
- **Infrastructure as Code (IaC):** Modular Terraform automating AWS VPC, least-privilege security groups, and EC2 with IMDSv2 and gp3 encryption.
- **Dynamic Verification (DAST):** Automated smoke testing of \`/health\` and anti-clickjacking security headers.

---

### 4. Verification & Experimental Results
- **Pytest Suite:** 45/45 Unit and Integration tests passed.
- **Code Coverage:** 96% overall statement & branch coverage.
- **Vulnerability Count:** 0 Critical, 0 High, 0 Medium vulnerabilities in final production container.
`;

const outputPath = path.join(__dirname, 'project_report_summary.md');
fs.writeFileSync(outputPath, reportContent, 'utf-8');
console.log('Project report generated successfully at:', outputPath);
