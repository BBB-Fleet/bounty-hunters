"""
BBB Fleet 2: Bounty Hunters — Shared Configuration & Master Registry
=====================================================================
Central configuration for all 12 Fleet 2 agents, master bounty sources,
specialist routing maps, and discovery rules.
"""

import os
from dataclasses import dataclass, field
from typing import List, Dict, Literal, TypedDict, Optional
from dotenv import load_dotenv

load_dotenv()

# ==============================================================================
# BBB FLEET MASTER BUG BOUNTY & PoC DOCTRINE (HARDCODED INSTRUCTION BASE)
# ==============================================================================
BUG_BOUNTY_DOCTRINE = """
=== MASTER BUG BOUNTY & PROOF OF CONCEPT (PoC) STANDARD ===

1. CORE MISSION & IDENTITY:
- You are an autonomous security research agent operating on behalf of the BBB Fleet.
- A Bug Bounty is a formal, authorized vulnerability disclosure process for Web3 protocols,
  smart contracts, and open-source platforms.
- Your objective is to discover genuine security vulnerabilities, quantify the exact
  impact/risk, and provide verified mathematical proof through code.

2. VULNERABILITY REPORTING REQUIREMENTS:
- Every finding must cite the exact vulnerable contract/file, line numbers, and state
  variables affected.
- Severity must be rigorously categorized: CRITICAL, HIGH, or MEDIUM.
- Never report generic descriptions. Explain the root mechanism e.g., reentrancy due to
  state update after external call, oracle staleness, missing access control.

3. PROOF OF CONCEPT PoC INTEGRITY & ANTI-FAILURE RULES:
- NEVER output theoretical print statements without execution logic. Such PoCs fail triage
  and are immediately rejected.
- A valid PoC must be an executable, deterministic script that:
    a) Initializes the target environment / contract interfaces.
    b) Captures baseline pre-exploit state and balances.
    c) Executes the sequence of malicious calls / state transitions.
    d) Asserts mathematical proof of exploit e.g., Attacker balance increased, Vault drained.

4. VALID PoC REFERENCE EXAMPLES:

[REQUIRED - VALID EXPLOIT STRUCTURE]:
 Environment: Foundry / Python Web3 fork
  1. State Setup: Deploy/Attach target contract & attacker contract
  2. Invariant Check: initial_vault_balance = vault.balance()
  3. Execution: attacker.triggerAttack{value: 1 ether}()
  4. Final Proof: assert vault.balance() == 0 and attacker.balance() > initial_attacker_balance
"""

# === Environment & Infrastructure Credentials ===
GROQ_API_KEY: Optional[str] = os.environ.get("GROQ_API_KEY")
NEON_CONNECTION_STRING: Optional[str] = os.environ.get("NEON_CONNECTION_STRING")
UPSTASH_REDIS_URL: Optional[str] = os.environ.get("UPSTASH_REDIS_URL")
UPSTASH_REDIS_TOKEN: Optional[str] = os.environ.get("UPSTASH_REDIS_TOKEN")
OLLAMA_BASE_URL: str = os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL: str = os.environ.get("OLLAMA_MODEL", "llama3")

# === 12-Agent Fleet Registry ===
AGENTS: Dict[int, str] = {
    1: "Bounty Intel Scraper (Scanner)",
    2: "Bounty ROI Evaluator & Invoice Submitter (Accountant)",
    3: "Cross-Chain Bounty Specialist (Bridge)",
    4: "DeFi Bounty Specialist (Lender)",
    5: "Gas Cost Estimator & SDK Dev (Gas Requester)",
    6: "Solana/Rust Bounty Specialist (Solana Ghost)",
    7: "Smart Contract Bounty Specialist (Minter)",
    8: "Sandbox Security Auditor & Firewall (Watchdog)",
    9: "Platform Submission Formatter (Broadcaster)",
    10: "Bounty Pipeline Orchestrator (Boss)",
    11: "Bounty Platform Scout (Closer)",
    12: "Forensics Evidence Collector (Evidence)",
}

# === Master List: AI-Friendly Bug Bounty Sources (12 Sources across 4 Tiers) ===
class BountySource(TypedDict):
    name: str
    url: str
    type: str


MASTER_BUG_BOUNTY_SOURCES: Dict[str, List[BountySource]] = {
    "TIER_1_FULLY_OPEN": [
        {
            "name": "disclose.io",
            "url": "https://disclose.io",
            "type": "Global VDP & Bug Bounty Directory",
        },
        {
            "name": "Open Bug Bounty",
            "url": "https://openbugbounty.org",
            "type": "Fully Public Platform",
        },
        {
            "name": "HuntBug",
            "url": "https://huntbug.com",
            "type": "Public Program Directory",
        },
        {
            "name": "BountiesAlert",
            "url": "https://bountiesalert.com",
            "type": "Public Program Feed",
        },
    ],
    "TIER_2_PUBLIC_LISTS": [
        {
            "name": "Bugcrowd Public",
            "url": "https://bugcrowd.com/programs",
            "type": "Public Program List",
        },
        {
            "name": "HackerOne Directory",
            "url": "https://hackerone.com/directory/programs",
            "type": "Public Directory",
        },
    ],
    "TIER_3_BROADCAST_FEEDS": [
        {
            "name": "disclose.io Twitter Feed",
            "url": "https://twitter.com/disclose_io",
            "type": "Social Broadcast Alert",
        },
        {
            "name": "HuntBug Discord Feed",
            "url": "https://discord.gg/huntbug",
            "type": "Webhook Feed",
        },
        {
            "name": "Open Bug Bounty Telegram",
            "url": "https://t.me/openbugbounty",
            "type": "Public Alert Feed",
        },
    ],
    "TIER_4_WEB3_PLATFORMS": [
        {
            "name": "Immunefi",
            "url": "https://immunefi.com",
            "type": "Web3 Bug Bounties",
        },
        {
            "name": "Code4rena",
            "url": "https://code4rena.com",
            "type": "Audit Contests",
        },
        {
            "name": "Sherlock",
            "url": "https://sherlock.xyz",
            "type": "Web3 Security Contests",
        },
    ],
}

BOUNTY_PLATFORMS: Dict[str, str] = {
    "disclose": "https://disclose.io",
    "openbugbounty": "https://openbugbounty.org",
    "huntbug": "https://huntbug.com",
    "bountiesalert": "https://bountiesalert.com",
    "bugcrowd": "https://bugcrowd.com",
    "hackerone": "https://hackerone.com",
    "immunefi": "https://immunefi.com",
    "code4rena": "https://code4rena.com",
    "sherlock": "https://sherlock.xyz",
}

# === Target / Vulnerability Discovery Rules ===
MINIMUM_EVIDENCE_FIELDS: List[str] = [
    "title",
    "description",
    "steps_to_reproduce",
    "evidence",
    "impact",
]

REQUIRED_TARGET_FIELDS: List[str] = [
    "platform",
    "program_name",
    "platform_url",
    "reward_info",
    "scope",
    "repo_url",
]

class DiscoveryRules(TypedDict):
    required_fields: List[str]
    minimum_evidence: List[str]


TARGET_DISCOVERY_RULES: DiscoveryRules = {
    "required_fields": REQUIRED_TARGET_FIELDS,
    "minimum_evidence": MINIMUM_EVIDENCE_FIELDS,
}

# Backward compatibility alias
VULNERABILITY_DISCOVERY_RULES: DiscoveryRules = TARGET_DISCOVERY_RULES

# === Bounty Types & Specialist Routing ===
BountyType = Literal[
    "smart_contract_audit",
    "defi_vulnerability",
    "cross_chain_bridge",
    "solana_rust",
    "sdk_tooling",
    "web_vulnerability",
]

BOUNTY_TYPES: List[BountyType] = [
    "smart_contract_audit",
    "defi_vulnerability",
    "cross_chain_bridge",
    "solana_rust",
    "sdk_tooling",
    "web_vulnerability",
]

SPECIALIST_MAPPING: Dict[BountyType, int] = {
    "smart_contract_audit": 7,  # Agent 7: Minter
    "defi_vulnerability": 4,    # Agent 4: Lender
    "cross_chain_bridge": 3,    # Agent 3: Bridge
    "solana_rust": 6,           # Agent 6: Solana Ghost
    "sdk_tooling": 5,           # Agent 5: Gas Requester
    "web_vulnerability": 7,     # Agent 7: Minter
}

# === Fleet 2: Run Schedule ===
TOTAL_DAILY_RUNS: int = 17
REAL_BOUNTY_RUNS_PER_DAY: int = TOTAL_DAILY_RUNS
CYCLE_INTERVAL_MINUTES: int = 85


# === Optional: Config object for centralized access ===
@dataclass(frozen=True)
class FleetConfig:
    doctrine: str = BUG_BOUNTY_DOCTRINE
    agents: Dict[int, str] = field(default_factory=lambda: AGENTS)
    bounty_sources: Dict[str, List[BountySource]] = field(
        default_factory=lambda: MASTER_BUG_BOUNTY_SOURCES
    )
    bounty_platforms: Dict[str, str] = field(default_factory=lambda: BOUNTY_PLATFORMS)
    discovery_rules: DiscoveryRules = field(default_factory=lambda: TARGET_DISCOVERY_RULES)
    bounty_types: List[BountyType] = field(default_factory=lambda: BOUNTY_TYPES)
    specialist_mapping: Dict[BountyType, int] = field(
        default_factory=lambda: SPECIALIST_MAPPING
    )
    total_daily_runs: int = TOTAL_DAILY_RUNS
    real_bounty_runs_per_day: int = REAL_BOUNTY_RUNS_PER_DAY
    cycle_interval_minutes: int = CYCLE_INTERVAL_MINUTES


FLEET_CONFIG = FleetConfig()
