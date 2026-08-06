"""
BBB Fleet 2: Bounty Hunters — Agent 1: Scanner (Bounty Intel Scraper)
=====================================================================
Phase 1 agent: Core Intake & Discovery.
Actively scans global tracking platforms (Tier 1 & Tier 4), prioritizes
based on potential ROI and complexity, and selects exactly 8 daily targets.
"""

import asyncio
import json
import random
from datetime import datetime
import aiohttp

AGENT_ID = 1
AGENT_NAME = "B2 Scanner"

# The approved automation-safe target platforms
TIER_1_SOURCES = [
    "https://disclose.io",
    "https://openbugbounty.org",
    "https://huntbug.com",
    "https://bountiesalert.com"
]

TIER_4_SOURCES = [
    "https://immunefi.com",
    "https://code4rena.com",
    "https://sherlock.xyz"
]

async def _fetch_text(url: str, max_chars: int = 5000) -> str:
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=15)) as resp:
                if resp.status == 200:
                    text = await resp.text()
                    return text[:max_chars]
    except Exception as e:
        return f"[Fetch error: {e}]"
    return ""


async def scrape_bug_platforms() -> list:
    """
    Mocked scraping of Tier 1 and Tier 4 platforms.
    In production, this would parse the specific HTML/JSON structure of each site.
    """
    print(f"[{AGENT_NAME}] Scraping Tier 1 and Tier 4 sources...")
    scraped_bounties = []
    
    # Simulate finding raw bounties across different platforms
    platforms = ["disclose.io", "immunefi", "code4rena", "sherlock", "openbugbounty"]
    severities = ["CRITICAL", "HARD", "MEDIUM", "EASY"]
    
    for i in range(25):  # Simulate finding 25 raw bounties
        plat = random.choice(platforms)
        sev = random.choice(severities)
        bounty = {
            "bounty_id": f"{plat.upper()}-{1000+i}",
            "title": f"[{plat}] Simulated {sev} Vulnerability #{i}",
            "platform": plat,
            "bounty_type": "smart_contract" if plat in ["immunefi", "code4rena", "sherlock"] else "web",
            "repo_url": f"https://github.com/example-org/target-repo-{i}",
            "commit_hash": "a1b2c3d4e5f6",
            "bounty_size_usd": random.randint(500, 100000),
            "tvl_usd": random.randint(10000, 5000000),
            "project_age_days": random.randint(10, 1000),
            "open_issues": random.randint(0, 100),
            "complexity_rating": random.randint(1, 10),
            "raw_severity": sev
        }
        scraped_bounties.append(bounty)
    
    return scraped_bounties


async def fetch_market_prices() -> dict:
    """Fetch current token prices from CoinGecko API."""
    print(f"[{AGENT_NAME}] Fetching market prices from CoinGecko...")
    # Mocking CoinGecko response
    return {"ETH": 3200.50, "USDC": 1.0, "SOL": 145.20}


async def extract_github_telemetry(repo_url: str) -> dict:
    """Isolate exact repository URL, target branch, and commit hash."""
    return {
        "repo_url": repo_url,
        "branch": "main",
        "commit_hash": "a1b2c3d4e5f67890" # Would be extracted via API in prod
    }


def calculate_priority_score(bounty: dict) -> float:
    """
    Calculate a prioritization score to rank bounties based on:
    Bounty size, TVL, project age, open issues, and complexity.
    """
    score = 0.0
    
    # Base score driven by payout potential
    score += bounty["bounty_size_usd"] * 0.01
    
    # TVL multiplier (higher TVL = more critical protocol)
    score += (bounty["tvl_usd"] / 100000) * 5
    
    # Complexity penalty (higher complexity = harder to solve)
    score -= bounty["complexity_rating"] * 10
    
    # Age factor (older projects = harder bugs to find)
    score -= (bounty["project_age_days"] * 0.1)
    
    return max(0.0, score)


def select_daily_targets(scored_bounties: list) -> list:
    """
    Selects the highest scoring 8 bounties, enforcing the distribution:
    2 Critical, 2 Hard, 2 Medium, 2 Easy.
    """
    targets = []
    
    # Group by severity
    buckets = {"CRITICAL": [], "HARD": [], "MEDIUM": [], "EASY": []}
    for b in scored_bounties:
        buckets[b["raw_severity"]].append(b)
        
    # Sort each bucket by priority score descending
    for sev in buckets:
        buckets[sev].sort(key=lambda x: x["priority_score"], reverse=True)
        
    # Select top 2 from each bucket
    for sev in buckets:
        targets.extend(buckets[sev][:2])
        
    return targets


async def run(comms, context: dict = None) -> list:
    """Main execution block for Scanner."""
    print(f"[{AGENT_NAME}] Phase 1: INTAKE & DISCOVERY Started.")
    
    # 1. Scrape platforms
    raw_bounties = await scrape_bug_platforms()
    
    # 2. Fetch prices (optional for scoring/ROI later)
    prices = await fetch_market_prices()
    
    # 3. Extract telemetry and score
    scored_bounties = []
    for b in raw_bounties:
        # Extract firm scope limits
        telemetry = await extract_github_telemetry(b["repo_url"])
        b["telemetry"] = telemetry
        
        # Calculate Priority Score
        b["priority_score"] = calculate_priority_score(b)
        b["state"] = "DISCOVERED"
        scored_bounties.append(b)
        
    # 4. Select top 8 targets
    daily_targets = select_daily_targets(scored_bounties)
    
    # 5. Transition state
    for t in daily_targets:
        t["state"] = "TRIAGED"
    
    print(f"[{AGENT_NAME}] Locked down {len(daily_targets)} high-priority targets for today's run.")
    
    if comms:
        await comms.save_pipeline_log("phase_1_intake", f"Scanner discovered and triaged {len(daily_targets)} targets.")
        
    return daily_targets


async def main():
    from core.bounty_comms import BountyComms
    comms = BountyComms(AGENT_ID, AGENT_NAME)
    await comms.startup()
    targets = await run(comms)
    for t in targets:
        print(f"  -> [{t['raw_severity']}] {t['title']} (Score: {t['priority_score']:.2f})")
    await comms.shutdown("Discovery completed", "", "")

if __name__ == "__main__":
    asyncio.run(main())
