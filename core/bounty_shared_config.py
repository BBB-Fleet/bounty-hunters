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
    1: 'Bounty Intel Scraper',
    2: 'Bounty ROI Evaluator',
    3: 'Cross-Chain Bounty Specialist',
    4: 'DeFi Bounty Specialist',
    5: 'Gas Cost Estimator',
    6: 'Solana/Rust Bounty Specialist',
    7: 'Smart Contract Bounty Specialist',
    8: 'Bounty Draft Security Auditor',
    9: 'Submission Formatter',
    10: 'Bounty Pipeline Orchestrator',
    11: 'Bounty Platform Scout'
}

BOUNTY_PLATFORMS = {
    'algora': 'https://api.algora.io/api',
    'github': 'https://api.github.com',
    'immunefi_feed': 'https://raw.githubusercontent.com/infosec-us-team/Immunefi-Bug-Bounty-Programs-Unofficial/main/projects.json'
}

MAX_CONSENSUS_TRIALS = 3

BOUNTY_TYPES = [
    'smart_contract_audit',
    'defi_vulnerability',
    'cross_chain_bridge',
    'solana_rust',
    'sdk_tooling',
    'documentation'
]

SPECIALIST_MAPPING = {
    'smart_contract_audit': 7,
    'defi_vulnerability': 4,
    'cross_chain_bridge': 3,
    'solana_rust': 6,
    'sdk_tooling': 11,
    'documentation': 9
}

# === Fleet 2: 16 Runs Per Day Schedule (90-Minute Interval Loop) ===
RUNS_PER_DAY = 16
CYCLE_INTERVAL_MINUTES = 90

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
FLEET 2 MISSION DIRECTIVE: Focus strictly on DISCOVERING and REPORTING novel bugs and security vulnerabilities on GitHub & Bug Bounty Platforms.
- DO NOT submit simple code formatting, docstring patches, or minor non-security PRs.
- PRIORITIZE: Smart contract reentrancy, access control bypasses, oracle manipulation, paymaster signature validation bugs, denial of service, and severe logic flaws.
- SUBMISSION REQUIREMENTS:
  1. Title & Vulnerability Type (Critical / High / Medium / Low)
  2. Affected Component / Function / File
  3. Proof-of-Concept / Exploit Scenario
  4. Impact Assessment & Recommended Remediation
"""

