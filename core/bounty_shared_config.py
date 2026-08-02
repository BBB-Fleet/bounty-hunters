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
