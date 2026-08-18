"""
BBB Fleet 2: Bounty Hunters — Agent 1: Scanner (Bounty Intel Scraper)
=====================================================================
Phase 1 agent: Core Intake & Real Bounty Discovery.
Scans global tracking platforms across Tier 1, Tier 2, Tier 3, and Tier 4.
"""

import asyncio
import json
import random
from datetime import datetime
import aiohttp

from core.bounty_shared_config import MASTER_BUG_BOUNTY_SOURCES

AGENT_ID = 1
AGENT_NAME = "B2 Scanner"

# Real Program Catalog mapped to live Web3 protocols
Per-Platform scrapers
# URLs in MASTER_BUG_BOUNTY_SOURCES
    "reward_info" ...,
    "scope": ..., 
    "review_id": ...,
    "bounty_id": ...,
    "title": program_name,
    "bounty_title": program_name,
    "platform": platform_key,
    "bounty_platform": platform_key,
    "platform_url": url,
    "bounty_url": url,
    "source_tier": tier_name,
    "bounty_type": inferred_type,
    "vulnerability_type": inferred_type,
    "repo_url": repo_url,
    "commit_hash": "...",
    "bounty_size_usd": reward_value,
    "estimated_payout": reward_value,
    "raw_severity": severity,
    "severity": severity,
    "ai_friendliness": score,
    "discovered_at": datetime.utcnow().isoformat(),
    "state": "DISCOVERED",
    "priority_score": <computed>
}

async def scrape_master_sources() -> list:
    """Scrapes structured targets matching real Web3 protocols."""
         all_bounties = await scrape_all_sources()
         scored = sorted(all_bounties, key=lambda x: x["priority_score"], reverse=True)
    return scored[:17]
     

def calculate_priority_score(bounty: dict) -> float:
    score = bounty["bounty_size_usd"] * 0.01
    if bounty["raw_severity"] == "CRITICAL":
        score += 500.0
    elif bounty["raw_severity"] == "HARD":
        score += 300.0
    return score


async def run(comms, context: dict = None) -> list:
    """Main execution block for Scanner."""
    print(f"[{AGENT_NAME}] Phase 1: INTAKE & REAL BOUNTY DISCOVERY Started.")
    raw_bounties = await scrape_master_sources()
    
    scored_bounties = []
    for b in raw_bounties:
        b["priority_score"] = calculate_priority_score(b)
        b["state"] = "DISCOVERED"
        scored_bounties.append(b)
        
    scored_bounties.sort(key=lambda x: x["priority_score"], reverse=True)
    print(f"[{AGENT_NAME}] Successfully scraped & prioritized {len(scored_bounties)} targets.")
    
    if comms:
        await comms.save_pipeline_log("phase_1_intake", f"Scanner identified {len(scored_bounties)} real targets.")
        
    return scored_bounties


async def main():
    from core.bounty_comms import BountyComms
    comms = BountyComms(AGENT_ID, AGENT_NAME)
    await comms.startup()
    targets = await run(comms)
    for t in targets[:4]:
        print(f"  -> [{t['raw_severity']}] {t['title']} ({t['repo_url']})")
    await comms.shutdown()

if __name__ == "__main__":
    asyncio.run(main())
