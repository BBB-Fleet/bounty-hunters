import os

from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.environ.get('GROQ_API_KEY')
NEON_CONNECTION_STRING = os.environ.get('NEON_CONNECTION_STRING')
UPSTASH_REDIS_URL = os.environ.get('UPSTASH_REDIS_URL')
UPSTASH_REDIS_TOKEN = os.environ.get('UPSTASH_REDIS_TOKEN')
OLLAMA_BASE_URL = os.environ.get('OLLAMA_BASE_URL', 'http://localhost:11434')
OLLAMA_MODEL = os.environ.get('OLLAMA_MODEL', 'llama3')
SPLITS_VAULT = os.environ.get('SPLITS_VAULT', '0xc87c3e8CB21e5A630Baf8D38b2060aCBb047afCb')
FLEET_PREFIX = 'bounty'

AGENTS = {
    1: 'Bounty Intel Scraper (Scanner)',
    2: 'Bounty ROI Evaluator & Invoice Submitter (Accountant)',
    3: 'Cross-Chain Bounty Specialist (Bridge)',
    4: 'DeFi Bounty Specialist (Lender)',
    5: 'Gas Cost Estimator & SDK Dev (Gas Requester)',
    6: 'Solana/Rust Bounty Specialist (Solana Ghost)',
    7: 'Smart Contract Bounty Specialist (Minter)',
    8: 'Sandbox Security Auditor & Firewall (Watchdog)',
    9: 'Platform Submission Formatter (Broadcaster)',
    10: 'Bounty Pipeline Orchestrator (Boss)',
    11: 'Bounty Platform Scout (Closer)',
    12: 'Forensics Evidence Collector (Evidence)'
}

# === MASTER LIST: AI-Friendly Bug Bounty Sources (No Login Required) ===
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
    'disclose': 'https://disclose.io',
    'openbugbounty': 'https://openbugbounty.org',
    'huntbug': 'https://huntbug.com',
    'bountiesalert': 'https://bountiesalert.com',
    'immunefi': 'https://immunefi.com',
    'code4rena': 'https://code4rena.com',
    'sherlock': 'https://sherlock.xyz'
}

MAX_CONSENSUS_TRIALS = 3

BOUNTY_TYPES = [
    'smart_contract_audit',
    'defi_vulnerability',
    'cross_chain_bridge',
    'solana_rust',
    'sdk_tooling',
    'web_vulnerability'
]

SPECIALIST_MAPPING = {
    'smart_contract_audit': 7,
    'defi_vulnerability': 4,
    'cross_chain_bridge': 3,
    'solana_rust': 6,
    'sdk_tooling': 5,
    'web_vulnerability': 1
}

# === Fleet 2: 17 Daily Runs Schedule (1 Practice Run + 16 Real Vulnerability Runs) ===
TOTAL_DAILY_RUNS = 17
PRACTICE_RUNS_PER_DAY = 1
REAL_BOUNTY_RUNS_PER_DAY = 16
CYCLE_INTERVAL_MINUTES = 85

# Legacy compatibility
RUNS_PER_DAY = TOTAL_DAILY_RUNS

# === Fleet 2: Daily Practice Repository Arena (Curated Targets Pool) ===
FLEET2_PRACTICE_CATALOG = [
    {
        "id": "B2-PRAC-001",
        "name": "Ethernaut - Reentrancy & Fallback Exploits",
        "category": "EVM Smart Contract Audit",
        "repo_url": "https://github.com/OpenZeppelin/ethernaut",
        "vulnerability_types": ["Reentrancy", "Access Control Bypass", "Fallback Function Misconfiguration"],
        "target_file": "contracts/levels/Reentrancy.sol"
    },
    {
        "id": "B2-PRAC-002",
        "name": "Damn Vulnerable DeFi - Unstoppable Vault Flaw",
        "category": "DeFi Flash Loan Vulnerability",
        "repo_url": "https://github.com/tinchoabbate/damn-vulnerable-defi",
        "vulnerability_types": ["Flash Loan Denial of Service", "Strict Balance Assertion", "State Desynchronization"],
        "target_file": "contracts/unstoppable/UnstoppableVault.sol"
    },
    {
        "id": "B2-PRAC-003",
        "name": "OWASP Web3 - Price Oracle Front-Running",
        "category": "DeFi Price Feed Security",
        "repo_url": "https://github.com/OWASP/www-project-web3-security-testing-guide",
        "vulnerability_types": ["Oracle Manipulation", "Spot Price Slippage Exploit", "Stale Feed Usage"],
        "target_file": "challenges/oracle_manipulation.sol"
    },
    {
        "id": "B2-PRAC-004",
        "name": "OpenZeppelin Account Abstraction - Paymaster Signature Bypass",
        "category": "ERC-4337 Smart Account Security",
        "repo_url": "https://github.com/eth-infinitism/account-abstraction",
        "vulnerability_types": ["Paymaster Signature Validation Failure", "Gas Drainage Exploit", "Replay Attack"],
        "target_file": "contracts/core/BasePaymaster.sol"
    },
    {
        "id": "B2-PRAC-005",
        "name": "Solana Anchor - Discriminator & Owner Check Bypass",
        "category": "Solana Rust Security",
        "repo_url": "https://github.com/coral-xyz/anchor",
        "vulnerability_types": ["Account Owner Validation Missing", "Anchor Discriminator Mismatch", "Signer Check Bypass"],
        "target_file": "programs/system/src/lib.rs"
    }
]

# === Fleet 2: Vulnerability-First Discovery Guidelines ===
VULNERABILITY_DISCOVERY_RULES = """
FLEET 2 MISSION DIRECTIVE: Target real bug bounties from the 12 Master AI-Friendly Sources (Tier 1..4).
- 17 Daily Runs: 1 Practice Run + 16 Real Vulnerability Discovery Runs.
- WATCHDOG: Creates private sandbox, guards against data leakage, verifies PoC, wipes sandbox.
- BOSS: Enforces 3-Trial Triple-Agreement Consensus (Trial 1: Execution, Trial 2: Peer Agreement, Trial 3: Unanimous Affirmation).
- BROADCASTER (Agent 9): Formats report to exact platform PDF standards.
- ACCOUNTANT (Agent 2): Signs off on financial ROI and commits to Neon `bbb_fleet_handoff`.
"""


