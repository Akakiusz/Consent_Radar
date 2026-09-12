# Consent Radar

An AI-assisted privacy auditor for your own network traffic.
It answers one question: **which domains are my apps quietly talking to?**

Consent Radar listens to your device's own outbound traffic, extracts the
domains being contacted (from DNS queries and TLS SNI — no decryption of
content), matches them against known tracker lists, and groups them into
categories on a live dashboard.

## Why

Most apps contact dozens of third-party domains in the background —
advertising, analytics, telemetry. This tool makes that visible in plain terms.

## How it works

1. **Capture** — reads domains from DNS/SNI on your own machine.
2. **Enrich** — flags each domain against public tracker lists.
3. **Classify** — groups domains and detects tracker-like behaviour.
4. **Dashboard** — shows who your apps talk to, and how often.

## Status

Early development. See milestones below.

- [x] Stage 0 — project scaffold
- [x] Stage 1 — traffic capture
- [ ] Stage 2 — tracker enrichment
- [ ] Stage 3 — ML classification layer
- [ ] Stage 4 — dashboard
- [ ] Stage 5 — polish & tests



## Installation

```bash
git clone https://github.com/Akakiusz/consent-radar.git
cd consent-radar
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```


## Limitations (honest notes)

- Sees **metadata only** (domain names), never the content of traffic.
- Capture requires elevated privileges — it does not "just run" for everyone.
- DNS-over-HTTPS may hide DNS queries; in that case only TLS SNI is visible.
- Only audit **your own** traffic. Capturing others' traffic is a legal/ethical issue.
- Much of the tracker labelling comes from public lists, not ML. The ML layer
  is used for pattern detection, not for the bulk classification.