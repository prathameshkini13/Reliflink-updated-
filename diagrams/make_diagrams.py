"""Generate publication-grade Architecture and CI/CD DevSecOps workflow diagrams.

Uses matplotlib with custom boxes, arrows, and styling to output:
  - diagrams/architecture.png
  - diagrams/cicd_workflow.png
"""
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

INK = "#0f172a"
C_APP = "#eff6ff"
C_SEC = "#fef2f2"
C_INFRA = "#fffbeb"
C_EXT = "#f8fafc"
C_OK = "#f0fdf4"
C_CI = "#f5f3ff"
BORDER_DARK = "#334155"


def box(ax, x, y, w, h, text, fc, fs=9, bold=False, ec=BORDER_DARK, lw=1.3, style="round,pad=0.02,rounding_size=0.08"):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle=style, fc=fc, ec=ec, lw=lw))
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=fs,
            fontweight="bold" if bold else "normal", color=INK, linespacing=1.25)


def arrow(ax, p1, p2, label="", rad=0.0, color="#334155", fs=7.5, off=(0, 0.12), ls="-"):
    ax.add_patch(FancyArrowPatch(p1, p2, arrowstyle="-|>", mutation_scale=12, lw=1.3, color=color,
                                 connectionstyle=f"arc3,rad={rad}", linestyle=ls))
    if label:
        ax.text((p1[0] + p2[0]) / 2 + off[0], (p1[1] + p2[1]) / 2 + off[1], label, ha="center", va="bottom",
                fontsize=fs, color=INK, bbox=dict(boxstyle="round,pad=0.12", fc="white", ec="none", alpha=0.9))


def generate_architecture_diagram(output_path):
    fig, ax = plt.subplots(figsize=(13.5, 7.5), dpi=300)
    ax.set_xlim(0, 13.5)
    ax.set_ylim(0, 7.5)
    ax.axis("off")
    ax.set_title("System Architecture — Disaster Relief Resource Allocation Platform (DevSecOps Edition)\n"
                 "Candidate: Kini Prathamesh Prakash (124BTCS1057) • CO2 • SDG 11: Sustainable Cities",
                 fontsize=12.5, fontweight="bold", pad=12, color=INK)

    # External Inputs
    box(ax, 0.3, 3.2, 1.8, 1.1, "Emergency Operative\n(Web Browser / UI)", C_EXT, 9, True)
    box(ax, 0.3, 5.5, 1.8, 1.0, "Disaster Sensor / CSV\n(Zones & Casualties)", C_EXT, 8.5)
    arrow(ax, (1.2, 5.5), (1.2, 4.3), "CSV Ingestion", off=(0.55, 0))

    # AWS Cloud Perimeter
    ax.add_patch(FancyBboxPatch((2.7, 0.4), 10.4, 6.7, boxstyle="round,pad=0.02,rounding_size=0.12",
                                fc="#fcfcfc", ec="#d97706", lw=2, linestyle="--"))
    ax.text(2.9, 6.85, "AWS Cloud Perimeter (ap-south-1 / Dedicated VPC 10.0.0.0/16) — Terraform Managed",
            fontsize=9.5, fontweight="bold", color="#b45309", va="center")

    # Security Group boundary
    box(ax, 3.0, 3.0, 2.0, 1.6, "Security Group\nInbound: TCP 80/443\nOutbound: HTTPS only\n(SSH Disallowed)", C_SEC, 8.5)
    arrow(ax, (2.1, 3.75), (3.0, 3.75), "HTTPS / TLS", off=(0, 0.14))

    # EC2 Instance
    ax.add_patch(FancyBboxPatch((5.4, 0.7), 7.4, 5.8, boxstyle="round,pad=0.02,rounding_size=0.1",
                                fc=C_INFRA, ec="#ea580c", lw=1.5))
    ax.text(5.6, 6.25, "AWS EC2 t3.micro · IMDSv2 Enforced · Encrypted gp3 EBS · Amazon Linux 2023",
            fontsize=8.5, fontweight="bold", color="#9a3412", va="center")
    arrow(ax, (5.0, 3.75), (5.4, 3.75))

    # Docker Hardened Container
    ax.add_patch(FancyBboxPatch((5.7, 1.0), 6.8, 4.9, boxstyle="round,pad=0.02,rounding_size=0.1",
                                fc="#e0f2fe", ec="#0284c7", lw=1.5))
    ax.text(5.9, 5.65, "Docker Hardened Container — Alpine Linux 3.20 (Non-root 'reliefapp' UID 10001, Read-only rootfs)",
            fontsize=8, fontweight="bold", color="#0369a1", va="center")

    # Inside container: Web Server
    box(ax, 6.0, 2.6, 2.4, 2.2, "Gunicorn 26 + Flask 3.1\n\n• CSRF Tokens (WTF)\n• CSP & Anti-Sniff\n• X-Frame: DENY\n• /health Probe",
        C_APP, 8, True, ec="#0284c7")

    # Inside container: Modular Core Engine (CO2)
    ax.add_patch(FancyBboxPatch((8.8, 1.3), 3.4, 3.9, boxstyle="round,pad=0.02,rounding_size=0.08",
                                fc="#f0fdf4", ec="#16a34a", lw=1.5))
    ax.text(9.0, 4.95, "Modular Allocation Engine (CO2)", fontsize=8.5, fontweight="bold", color="#15803d", va="center")

    box(ax, 9.0, 3.9, 3.0, 0.85, "Module 1 & 2: Triage Engine\n(Severity & Urgency Window)", C_EXT, 7.5)
    box(ax, 9.0, 2.8, 3.0, 0.85, "Module 3: Supply Optimizer\n(Water, Food, Med, Shelters)", C_EXT, 7.5)
    box(ax, 9.0, 1.7, 3.0, 0.85, "Module 4 & 5: SDG 11 & Alerts\n(Carbon Savings & Dispatch)", C_EXT, 7.5)

    arrow(ax, (8.4, 3.7), (8.8, 3.7), "Internal API", off=(0, 0.12))

    plt.tight_layout()
    fig.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close(fig)
    print(f"Architecture diagram generated: {output_path}")


def generate_cicd_diagram(output_path):
    fig, ax = plt.subplots(figsize=(14.5, 6.0), dpi=300)
    ax.set_xlim(0, 14.5)
    ax.set_ylim(0, 6.0)
    ax.axis("off")
    ax.set_title("DevSecOps CI/CD Pipeline Workflow — Shift-Left Automated Quality & Security Gates\n"
                 "Candidate: Kini Prathamesh Prakash (124BTCS1057) • Jenkins Declarative Pipeline",
                 fontsize=12.5, fontweight="bold", pad=12, color=INK)

    stages = [
        ("1. Git Commit\n& Checkout", C_EXT, "Feature / Main Branch"),
        ("2. Static Code\nLinting & Flake8", C_APP, "PEP8 & Style Guard"),
        ("3. Unit Tests\n& Coverage", C_APP, "pytest-cov (>95%)"),
        ("4. SonarQube\nSAST Analysis", C_SEC, "Bugs & Hotspots"),
        ("5. Quality\nGate", C_OK, "Wait for Gate Status"),
        ("6. Trivy SCA &\nSecret Scan", C_SEC, "Dependencies & Keys"),
        ("7. Build Docker\nMulti-stage", C_CI, "Alpine non-root"),
        ("8. Trivy Image\nCVE Scan", C_SEC, "0 Critical / 0 High"),
        ("9. Push to\nAWS ECR", C_INFRA, "Tagged Build No."),
        ("10. Terraform\nAWS Deploy", C_INFRA, "VPC / EC2 / SG"),
        ("11. DAST &\nHealth Smoke", C_OK, "Verify Live App"),
    ]

    x_start = 0.3
    w = 1.05
    h = 2.2
    gap = 0.24
    y = 1.8

    for i, (title, color, desc) in enumerate(stages):
        x = x_start + i * (w + gap)
        box(ax, x, y, w, h, f"{title}\n\n{desc}", color, 7.5, bold=True)
        if i < len(stages) - 1:
            arrow(ax, (x + w, y + h / 2), (x + w + gap, y + h / 2), color="#2563eb")

    # Legend at bottom
    ax.text(0.5, 0.7, "Security & Quality Gate Checkpoints: ", fontsize=8.5, fontweight="bold", color=INK)
    box(ax, 3.8, 0.45, 1.8, 0.55, "SAST / SCA Scan", C_SEC, 7.5)
    box(ax, 5.8, 0.45, 1.8, 0.55, "Passing Quality Gate", C_OK, 7.5)
    box(ax, 7.8, 0.45, 1.8, 0.55, "Container Build / Deploy", C_INFRA, 7.5)

    plt.tight_layout()
    fig.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close(fig)
    print(f"CI/CD workflow diagram generated: {output_path}")


if __name__ == "__main__":
    diagram_dir = os.path.dirname(os.path.abspath(__file__))
    generate_architecture_diagram(os.path.join(diagram_dir, "architecture.png"))
    generate_cicd_diagram(os.path.join(diagram_dir, "cicd_workflow.png"))
