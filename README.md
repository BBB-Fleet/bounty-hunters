# BBB Fleet 2: The Bounty Hunters (Mercenary Squad)

> **LEGAL NOTICE**: This repository and all code, architectures, agent outputs, and consensus workflows contained herein are the exclusive intellectual property of **Blade Yerby** and are governed under the [Master Creator License Stack v2 (MCLS v2)](./MCLS_v2_LICENSE.md). By accessing this repository you agree to all terms including Section 11 Clickwrap Assent.

---

**Architect**: Blade Yerby  
**Fleet Model**: BBB-Fleet (2) -- 11 Autonomous Mercenary Units  
**Governing License**: [MCLS v2 & Nine Doctrines](./MCLS_v2_LICENSE.md)  
**Mercenary Vault**: `0xc87c3e8CB21e5A630Baf8D38b2060aCBb047afCb` ([Splits.org](https://splits.org))  

---

## Architectural Overview

BBB Fleet 2 operates purely on logic, zero capital, and strict peer consensus. The fleet is a cloud-based autonomous bounty hunting system that discovers, analyzes, solves, and submits bounties across Web3 platforms.

### 7-Phase Bounty Pipeline

| Phase | Name | Lead Agent | Description |
|-------|------|-----------|-------------|
| 1 | **The Hunt** | Agent 11 (Scout) | Scans Algora, GitHub, and Immunefi for active bounties |
| 2 | **Internal Approval** | Agent 10 (Boss) + Agent 2 (Accountant) | Evaluates ROI and compute cost vs payout |
| 3 | **Intel Gathering** | Agent 1 (Scanner) | Scrapes raw source code, READMEs, and documentation |
| 4 | **The War Room** | Specialist (3-7) + Agent 8 (Watchdog) | Domain specialist drafts solution; Watchdog audits |
| 5 | **Consensus Loop** | All Participants | 100% AGREE vote required. Max 3 trials |
| 6 | **Packaging** | Agent 9 (Broadcaster) | Formats platform-specific submission payload |
| 7 | **Invoice & Handoff** | Agent 2 (Accountant) | Submits to Fleet 1 review bridge via `bbb_fleet_handoff` |

### The 11 Mercenary Agents

| ID | Codename | Specialty |
|----|----------|-----------|
| 1 | Scanner | Bounty Intel Scraper |
| 2 | Accountant | ROI Evaluator & Invoice Submitter |
| 3 | Bridge | Cross-Chain Bounty Specialist |
| 4 | Lender | DeFi / Lending Protocol Specialist |
| 5 | Gas Requester | Gas Cost Estimator & SDK Dev |
| 6 | Solana Ghost | Solana / Rust / Anchor Specialist |
| 7 | Minter | EVM Smart Contract Specialist |
| 8 | Watchdog | Independent Security Auditor |
| 9 | Broadcaster | Submission Formatter |
| 10 | Boss | Pipeline Orchestrator |
| 11 | Closer | Bounty Platform Scout |

---

## Infrastructure

- **Compute**: GitHub Actions (free tier, 2000 min/month)
- **LLM**: Groq API free tier (llama-3.1-8b-instant)
- **Database**: Neon Postgres (`bounty_` table prefix)
- **Cache**: Upstash Redis (`bounty:` key prefix)
- **Payout**: Splits.org Mercenary Vault

---

## Legal Protection

This codebase is protected under the **Master Creator License Stack v2 (MCLS v2)**:

- **Doctrine 5 (Anti-Dilution)**: No third party may claim co-ownership through fork or contribution.
- **Doctrine 6 (Blueprint Intent)**: Architect retains 100% IP and vault revenue ownership.
- **Doctrine 7 (Bioprinter Organism)**: Fleet acts as a living digital organism; underlying LLMs are computational tools, not co-creators.
- **Section 11 (Clickwrap Assent)**: Access to this repository constitutes acceptance of all license terms.

See [MCLS_v2_LICENSE.md](./MCLS_v2_LICENSE.md) for full terms.

---

*Copyright (c) 2026 Blade Yerby. All Rights Reserved.*
