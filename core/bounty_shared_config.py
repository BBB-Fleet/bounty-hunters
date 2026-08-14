"""
BBB Fleet 2: Bounty Hunters — Shared Configuration & Master Registry
=====================================================================
Central configuration for all 12 Fleet 2 agents, master bounty sources,
specialist routing maps, practice catalog, and discovery rules.
"""

import os
from dotenv import load_dotenv

load_dotenv()

# === Environment & Infrastructure Credentials ===
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
NEON_CONNECTION_STRING = os.environ.get("NEON_CONNECTION_STRING")
UPSTASH_REDIS_URL = os.environ.get("UPSTASH_REDIS_URL")
UPSTASH_REDIS_TOKEN = os.environ.get("UPSTASH_REDIS_TOKEN")
OLLAMA_BASE_URL = os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "llama3")
SPLITS_VAULT = os.environ.get("SPLITS_VAULT", "0xc87c3e8CB21e5A630Baf8D38b2060aCBb047afCb")
FLEET_PREFIX = "bounty"

# === 12-Agent Fleet Registry ===
AGENTS = {
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
    12: "Forensics Evidence Collector (Evidence)"
}

# === Master List: AI-Friendly Bug Bounty Sources (12 Sources across 4 Tiers) ===
MASTER_BUG_BOUNTY_SOURCES = {
    "TIER_1_FULLY_OPEN": [
        {"name": "disclose.io", "url": "https://disclose.io", "type": "Global VDP & Bug Bounty Directory", "ai_friendliness": 5},
        {"name": "Open Bug Bounty", "url": "https://openbugbounty.org", "type": "Fully Public Platform", "ai_friendliness": 5},
        {"name": "HuntBug", "url": "https://huntbug.com", "type": "Public Program Directory", "ai_friendliness": 5},
        {"name": "BountiesAlert", "url": "https://bountiesalert.com", "type": "Public Program Feed", "ai_friendliness": 5}
    ],
    "TIER_2_PUBLIC_LISTS": [
        {"name": "Bugcrowd Public", "url": "https://bugcrowd.com/programs", "type": "Public Program List", "ai_friendliness": 3},
        {"name": "HackerOne Directory", "url": "https://hackerone.com/directory/programs", "type": "Public Directory", "ai_friendliness": 2}
    ],
    "TIER_3_BROADCAST_FEEDS": [
        {"name": "disclose.io Twitter Feed", "url": "https://twitter.com/disclose_io", "type": "Social Broadcast Alert", "ai_friendliness": 4},
        {"name": "HuntBug Discord Feed", "url": "https://discord.gg/huntbug", "type": "Webhook Feed", "ai_friendliness": 4},
        {"name": "Open Bug Bounty Telegram", "url": "https://t.me/openbugbounty", "type": "Public Alert Feed", "ai_friendliness": 4}
    ],
    "TIER_4_WEB3_PLATFORMS": [
        {"name": "Immunefi", "url": "https://immunefi.com", "type": "Web3 Bug Bounties", "ai_friendliness": 5},
        {"name": "Code4rena", "url": "https://code4rena.com", "type": "Audit Contests", "ai_friendliness": 5},
        {"name": "Sherlock", "url": "https://sherlock.xyz", "type": "Web3 Security Contests", "ai_friendliness": 5}
    ]
}

BOUNTY_PLATFORMS = {
    "disclose": "https://disclose.io",
    "openbugbounty": "https://openbugbounty.org",
    "huntbug": "https://huntbug.com",
    "bountiesalert": "https://bountiesalert.com",
    "Bugcrowd": "https://bugcrowd.com",
    "HackerOne": "https://hackerone.com",
    "immunefi": "https://immunefi.com",
    "code4rena": "https://code4rena.com",
    "sherlock": "https://sherlock.xyz"
}

TARGET_DISCOVERY_RULES = {
    "required_fields": [
        "platform",
        "program_name",
        "platform_url",
        "reward_info",
        "scope",
        "repo_url"
    ],
    "disallowed_generated_fields": [
        "fake_vulnerability",
        "fake_severity",
        "fake_payout"
    ],
    "minimum_evidence": [
        "public_program_page",
        "public_scope_page",
        "bounty_name"
    ],
    "extract": [
        "repositories",
        "documentation",
        "contracts",
        "targets",
        "assets",
        "reward_ranges"
    ]
}

# Backward compatibility alias
VULNERABILITY_DISCOVERY_RULES = TARGET_DISCOVERY_RULES

BOUNTY_TYPES = [
    "smart_contract_audit",
    "defi_vulnerability",
    "cross_chain_bridge",
    "solana_rust",
    "sdk_tooling",
    "web_vulnerability"
]

# Specialist routing to Agents 3, 4, 5, 6, 7
SPECIALIST_MAPPING = {
    "smart_contract_audit": 7,  # Agent 7: Minter
    "defi_vulnerability": 4,    # Agent 4: Lender
    "cross_chain_bridge": 3,    # Agent 3: Bridge
    "solana_rust": 6,           # Agent 6: Solana Ghost
    "sdk_tooling": 5,           # Agent 5: Gas Requester
    "web_vulnerability": 7      # Agent 7: Minter
}

# === Fleet 2: 17 Daily Runs Schedule (1 Practice + 16 Real Vulnerability Runs) ===
TOTAL_DAILY_RUNS = 17
PRACTICE_RUNS_PER_DAY = 1
REAL_BOUNTY_RUNS_PER_DAY = 16
CYCLE_INTERVAL_MINUTES = 85
RUNS_PER_DAY = TOTAL_DAILY_RUNS

# === Daily Practice Arena Curated Targets ===
FLEET2_PRACTICE_CATALOG = [
    {
        "id": "B2-PRAC-001",
        "name": "Ethernaut - Reentrancy & Fallback Exploits",
        "category": "smart_contract_audit",
        "bounty_type": "smart_contract_audit",
        "repo_url": "https://github.com/OpenZeppelin/ethernaut",
        "platform": "practice_arena",
        "platform_url": "https://ethernaut.openzeppelin.com",
        "vulnerability_types": ["Reentrancy", "Access Control Bypass", "Fallback Function Misconfiguration"],
        "target_file": "contracts/levels/Reentrancy.sol",
        "reward_info": "Practice Run ($0)",
        "scope": ["contracts/levels/Reentrancy.sol"],
        "ai_friendliness": 5
    },
    {
        "id": "B2-PRAC-002",
        "name": "Damn-Vulnerable-DeFi - Unstoppable Vault",
        "category": "defi_vulnerability",
        "bounty_type": "defi_vulnerability",
        "repo_url": "https://github.com/tinchoabbate/damn-vulnerable-defi",
        "platform": "practice_arena",
        "platform_url": "https://damnvulnerabledefi.xyz",
        "vulnerability_types": ["Flash loan invariant balance check desynchronization", "Strict equality DOS"],
        "target_file": "contracts/unstoppable/UnstoppableVault.sol",
        "reward_info": "Practice Run ($0)",
        "scope": ["contracts/unstoppable/UnstoppableVault.sol"],
        "ai_friendliness": 5
    },
    {
        "id": "B2-PRAC-003",
        "name": "Wormhole Bridge Invariant Test Suite",
        "category": "cross_chain_bridge",
        "bounty_type": "cross_chain_bridge",
        "repo_url": "https://github.com/wormhole-foundation/wormhole",
        "platform": "practice_arena",
        "platform_url": "https://wormhole.com",
        "vulnerability_types": ["Cross-Chain Message Verification", "Signature Desynchronization"],
        "target_file": "ethereum/contracts/bridge/Bridge.sol",
        "reward_info": "Practice Run ($0)",
        "scope": ["ethereum/contracts/bridge/Bridge.sol"],
        "ai_friendliness": 5
    }
]

