/**
 * Viva & Project Evaluation Cheatsheet Generator
 */
const fs = require('fs');
const path = require('path');

const cheatsheet = `# Evaluation & Viva Quick Reference Cheatsheet

**Candidate:** Kini Prathamesh Prakash (124BTCS1057)  
**Topic:** Modular Design of a Disaster Relief Resource Allocation Platform  
**Course Outcome:** CO2 | Review 6 | PSO2  

### Common Reviewer Questions & Model Answers

**Q1: How does your modular design satisfy Course Outcome CO2?**
- *Answer:* The platform is engineered into five decoupled modules: \`validate_disaster_report\` (checks data boundaries and disaster requirements), \`calculate_triage_score\` (ranks urgency), \`allocate_resources\` (satisfies Sphere humanitarian quotas), \`evaluate_sustainability\` (calculates carbon footprint and SDG 11 metrics), and \`generate_dispatch_alert\` (detects stock deficits).

**Q2: How does the platform address UN SDG 11 (Sustainable Cities and Communities)?**
- *Answer:* Target 11.5 aims to decrease direct disaster economic loss and mortality. Our Module 4 enforces green relief logistics: optimizing payload weights to minimize freight emissions and replacing diesel generators with portable solar units, preventing ~13.5 kg CO2 emissions per unit daily.

**Q3: How does the DevSecOps pipeline differ from standard DevOps?**
- *Answer:* DevSecOps shifts security left. Rather than scanning at runtime, our pipeline performs static analysis (SonarQube) during build, scans dependencies and secrets with Trivy before container creation, scans container images for CVEs before pushing to AWS ECR, and tests security headers dynamically.

**Q4: Why was Alpine Linux selected over Debian slim for the Docker container?**
- *Answer:* The Debian-slim base image had 172 vulnerabilities due to systemd and util-linux packages. Alpine Linux 3.20 has a drastically smaller attack surface, zero systemd footprint, and allows pip and compilers to be completely excluded from the runtime image, achieving 0 Critical and 0 High CVEs.

**Q5: What cloud security controls are provisioned via Terraform?**
- *Answer:* Terraform enforces IMDSv2 (\`http_tokens = "required"\`) to neutralize SSRF attacks, encrypts root EBS volumes using AES-256 gp3, eliminates open SSH ports by relying on AWS SSM, and limits outbound traffic to secure HTTPS.
`;

const csPath = path.join(__dirname, 'cheatsheet.md');
fs.writeFileSync(csPath, cheatsheet, 'utf-8');
console.log('Cheatsheet generated at:', csPath);
