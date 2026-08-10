# BBB Fleet 2: The Bounty Hunters (Mercenary Squad)

> **LEGAL NOTICE**: This repository and all code, architectures, agent outputs, and consensus workflows contained herein are the exclusive intellectual property of **Blade Yerby** and are governed under the [Master Creator License Stack v2 (MCLS v2)](./MCLS_v2_LICENSE.md). By accessing this repository you agree to all terms including Section 11 Clickwrap Assent.

---

**Architect**: Blade Yerby  
**Fleet Model**: BBB-Fleet (2) -- 12 Autonomous Mercenary Units  
**Governing License**: [MCLS v2 & Nine Doctrines](./MCLS_v2_LICENSE.md)  
**Mercenary Vault**: `0xc87c3e8CB21e5A630Baf8D38b2060aCBb047afCb` ([Splits.org](https://splits.org))  

---

## Architectural Overview

BBB Fleet 2 operates purely on logic, zero capital, and strict peer consensus. The fleet is a cloud-based autonomous bounty hunting system that discovers, analyzes, solves, and submits real bounties across open AI-friendly bug bounty platforms.

### 17-Run Daily Schedule

Fleet 2 operates on a **17-Run Daily Cycle** (~85-minute interval loop):
- **1 Practice Run** (Cycle 1): Curated Daily Target Arena for continuous model alignment and validation.
- **16 Real Vulnerability Runs** (Cycles 2–17): Real money-generating vulnerability discovery across the 12 Master Sources (1 vulnerability hunt per run).

---

### Master List of Bug Bounty Sources (12 Sources across 4 Tiers)

| Tier | Category | Approved Sources | AI Friendliness |
|------|----------|------------------|-----------------|
| **Tier 1** | Fully Open & Scrape-Friendly | `disclose.io`, `Open Bug Bounty`, `HuntBug`, `BountiesAlert` | ⭐⭐⭐⭐⭐ |
| **Tier 2** | Public Directories | `Bugcrowd Public`, `HackerOne Directory` | ⭐⭐⭐ |
| **Tier 3** | Broadcast Feeds | `disclose.io Twitter/X`, `HuntBug Discord`, `Open Bug Bounty Telegram` | ⭐⭐⭐⭐ |
| **Tier 4** | Web3 Platforms | `Immunefi`, `Code4rena`, `Sherlock` | ⭐⭐⭐⭐⭐ |

---

### 7-Phase Bounty Pipeline

| Phase | Name | Lead Agent | Description |
|-------|------|-----------|-------------|
| 1 | **The Hunt** | Agent 1 (Scanner) + Agent 11 (Scout) | Scans Master List sources (Tier 1..4) for real bug bounties |
| 2 | **Internal Approval** | Agent 10 (Boss) + Agent 2 (Accountant) | Evaluates ROI and compute cost vs payout potential |
| 3 | **Intel & Target Intake** | Agent 1 (Scanner) | Scrapes target source code, documentation, and AST telemetry |
| 4 | **Sandbox & War Room** | Specialists (3–7) + Agent 8 (Watchdog) | Watchdog builds private sandbox, guards firewall against data leakage, specialists write PoC |
| 5 | **3-Trial Consensus** | Agent 10 (Boss) | 3-Trial Consensus: 1. Did it work? 2. Peer agreement? 3. Unanimous 3rd try pass (100% agreement or DENIED) |
| 6 | **Platform Formatting** | Agent 9 (Broadcaster) | Formats report layout to match target platform standards (Immunefi, Code4rena, Sherlock, disclose.io) for PDF rendering |
| 7 | **Handoff & Invoice** | Agent 2 (Accountant) + Agent 11 (Closer) | Wipes sandbox cleanly, signs SHA-256 evidence chain, and commits to Neon `bbb_fleet_handoff` for Fleet 1 |

---

### The 12 Mercenary Agents

| ID | Codename | Specialty & Architectural Role |
|----|----------|--------------------------------|
| 1 | Scanner | Real Bug Bounty Source Scraper & Intake |
| 2 | Accountant | Financial ROI Evaluator & Neon Handoff Submitter |
| 3 | Bridge | Cross-Chain / Bridge Vulnerability Specialist |
| 4 | Lender | DeFi & Lending Protocol Specialist |
| 5 | Gas Requester | Gas Estimator & Dev Tooling Specialist |
| 6 | Solana Ghost | Solana / Rust / Anchor Security Specialist |
| 7 | Minter | EVM & Solidity Smart Contract Specialist |
| 8 | Watchdog | Private Sandbox Builder, Firewall Guard & Sandbox Teardown Auditor |
| 9 | Broadcaster | Platform Submission Formatter (Immunefi, Code4rena, Sherlock, disclose.io) |
| 10 | Boss | Pipeline Orchestrator & 3-Trial Unanimous Consensus Verifier |
| 11 | Closer | Bounty Platform Scout & State Machine Gatekeeper |
| 12 | Evidence | Forensics Evidence Collector & SHA-256 Chain-of-Evidence Builder |

---

## Infrastructure

- **Compute**: GitHub Actions / Cloud Runner
- **LLM**: Groq API free tier / Ollama local
- **Database**: Neon Postgres (`bounty_` table prefix & `bbb_fleet_handoff`)
- **Cache**: Upstash Redis (`bounty:` key prefix)
- **Payout**: Splits.org Mercenary Vault (`0xc87c3e8CB21e5A630Baf8D38b2060aCBb047afCb`)

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

