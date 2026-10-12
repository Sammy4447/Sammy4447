#!/usr/bin/env python3
"""Generate the animated DEVOPS tech-stack banner as a self-contained SVG.

Tool logos (from devicon) ride around an infinity loop behind a big "DEVOPS".
Logos are embedded as data URIs because GitHub won't load external images
inside an SVG.

Usage: python3 scripts/gen_stack.py assets/devops.svg
"""
import base64
import math
import re
import sys
import urllib.request

DEVICON = "https://cdn.jsdelivr.net/gh/devicons/devicon@v2.16.0/icons/{}.svg"

# devicon paths, in the order they travel round the loop
TOOLS = [
    "amazonwebservices/amazonwebservices-original-wordmark",
    "docker/docker-original",
    "github/github-original",
    "kubernetes/kubernetes-original",
    "terraform/terraform-original",
    "linux/linux-original",
    "jenkins/jenkins-original",
    "grafana/grafana-original",
    "githubactions/githubactions-original",
    "ansible/ansible-original",
    "prometheus/prometheus-original",
    "git/git-original",
    "argocd/argocd-original",
    "nginx/nginx-original",
    "redhat/redhat-original",
    "helm/helm-original",
    "gitlab/gitlab-original",
    "python/python-original",
    "bash/bash-original",
    "vault/vault-original",
]

W, H = 1000, 440
CX, CY = W / 2, H / 2
LOOP_A = 435     # half-width of the infinity loop
LAP = 40         # seconds for a logo to go once round the loop
CHIP_R = 31      # logo chip radius
LOGO = 40        # logo size inside the chip
GREEN = "#39ff14"


def fetch_icon(path: str) -> str:
    with urllib.request.urlopen(DEVICON.format(path), timeout=20) as r:
        svg = r.read().decode()
    if re.search(r"<script|\son\w+\s*=|<foreignObject", svg, re.I):
        raise ValueError(f"refusing suspicious icon: {path}")
    svg = re.sub(r"<\?xml.*?\?>|<!--.*?-->", "", svg, flags=re.S).strip()
    return "data:image/svg+xml;base64," + base64.b64encode(svg.encode()).decode()


def infinity_path(steps: int = 160) -> str:
    # Lemniscate of Bernoulli
    pts = []
    for k in range(steps + 1):
        t = 2 * math.pi * k / steps
        d = 1 + math.sin(t) ** 2
        x = CX + LOOP_A * math.cos(t) / d
        y = CY + LOOP_A * math.sin(t) * math.cos(t) / d
        pts.append(f"{x:.1f},{y:.1f}")
    return "M" + " L".join(pts) + "Z"


def build() -> str:
    path = infinity_path()
    chips = []
    for i, tool in enumerate(TOOLS):
        begin = -LAP * i / len(TOOLS)
        chips.append(f"""<g>
  <circle r="{CHIP_R}" fill="#f6f8fa" stroke="{GREEN}" stroke-opacity="0.7" stroke-width="2"/>
  <image href="{fetch_icon(tool)}" x="{-LOGO / 2}" y="{-LOGO / 2}" width="{LOGO}" height="{LOGO}"/>
  <animateMotion dur="{LAP}s" begin="{begin:.2f}s" repeatCount="indefinite"><mpath href="#loop"/></animateMotion>
</g>""")

    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="DevOps tech stack">
<title>DevOps tech stack</title>
<defs>
  <pattern id="dots" width="16" height="16" patternUnits="userSpaceOnUse">
    <circle cx="8" cy="8" r="1.6" fill="#13241a"/>
  </pattern>
  <linearGradient id="shine" gradientUnits="userSpaceOnUse" x1="-400" y1="0" x2="0" y2="0">
    <stop offset="0" stop-color="#8b949e"/>
    <stop offset="0.5" stop-color="#e6edf3"/>
    <stop offset="1" stop-color="#8b949e"/>
    <animateTransform attributeName="gradientTransform" type="translate" from="0 0" to="{W + 400} 0" dur="5s" repeatCount="indefinite"/>
  </linearGradient>
  <filter id="glow" x="-20%" y="-20%" width="140%" height="140%">
    <feGaussianBlur stdDeviation="3" result="b"/>
    <feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>
  </filter>
  <path id="loop" d="{path}"/>
</defs>
<rect width="{W}" height="{H}" rx="18" fill="#0b0f0b"/>
<rect width="{W}" height="{H}" rx="18" fill="url(#dots)"/>
<use href="#loop" fill="none" stroke="{GREEN}" stroke-opacity="0.35" stroke-width="2" stroke-dasharray="6 10" filter="url(#glow)">
  <animate attributeName="stroke-dashoffset" from="0" to="-160" dur="4s" repeatCount="indefinite"/>
</use>
<text x="{CX}" y="{CY + 62}" text-anchor="middle" textLength="840" lengthAdjust="spacingAndGlyphs"
      font-family="'Arial Black', 'Helvetica Neue', Arial, sans-serif" font-weight="900" font-size="180"
      fill="url(#shine)" fill-opacity="0.92">DEVOPS</text>
{"".join(chips)}
</svg>
"""


if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else "assets/devops.svg"
    with open(out, "w") as f:
        f.write(build())
    print(f"wrote {out}")
