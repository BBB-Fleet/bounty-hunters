"""
BBB Fleet 2: Bounty Hunters — Agent 11: The Closer (Bounty Platform Scout)
===========================================================================
Phase 1 agent. Scrapes bounty platforms (Algora, GitHub Issues, Immunefi)
for open opportunities the fleet can tackle.
"""

import asyncio
import json
import os
from datetime import datetime

import aiohttp

AGENT_ID = 11
AGENT_NAME = "B2 Closer"


async def _fetch_json(url: str, headers: dict = None, timeout: int = 15) -> dict | list | None:
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers or {}, timeout=aiohttp.ClientTimeout(total=timeout)) as resp:
                if resp.status == 200:
                    return await resp.json()
    except Exception as e:
        print(f"[{AGENT_NAME}] Fetch error {url}: {e}")
    return None


async def scan_algora() -> list:
    """Scan Algora for open bounties."""
    bounties = []
    orgs = ["electric-capital", "starkware", "ethereum", "solana-labs", "paradigm-xyz"]
    for org in orgs:
        url = f"https://api.algora.io/api/orgs/{org}/bounties"
        data = await _fetch_json(url)
        if data and isinstance(data, list):
            for b in data[:3]:
                bounties.append({
                    "platform": "algora",
                    "bounty_id": f"algora-{b.get('id', 'unknown')}",
                    "title": b.get("title", "Untitled")[:200],
                    "description": str(b.get("body", b.get("description", "")))[:500],
                    "payout_range": b.get("reward", {}).get("amount", "Unknown"),
                    "repo_url": b.get("html_url", b.get("url", "")),
                    "deadline": b.get("deadline", None),
                    "bounty_type": "sdk_tooling",
                    "status": "open"
                })
    return bounties


async def scan_github_bounties(token: str = None) -> list:
    """Search GitHub for issues labeled 'bounty'."""
    bounties = []
    headers = {"Accept": "application/vnd.github+json", "User-Agent": "BBB-BountyHunters"}
    if token and isinstance(token, str) and token.strip() and token != "None":
        headers["Authorization"] = f"Bearer {token.strip()}"
    url = "https://api.github.com/search/issues?q=label:bounty+state:open+sort:created&per_page=10"
    data = await _fetch_json(url, headers)
    if data and "items" in data:
        for item in data["items"][:5]:
            repo_url = item.get("repository_url", "").replace("api.github.com/repos", "github.com")
            bounties.append({
                "platform": "github",
                "bounty_id": f"gh-{item.get('number', 0)}",
                "title": item.get("title", "")[:200],
                "description": str(item.get("body", ""))[:500],
                "payout_range": "Varies",
                "repo_url": item.get("html_url", ""),
                "deadline": None,
                "bounty_type": "sdk_tooling",
                "status": "open"
            })
    return bounties


async def scan_immunefi() -> list:
    """Scan Immunefi unofficial JSON feed for active programs."""
    bounties = []
    url = "https://raw.githubusercontent.com/infosec-us-team/Immunefi-Bug-Bounty-Programs-Unofficial/main/projects.json"
    data = await _fetch_json(url, timeout=30)
    if data and isinstance(data, list):
        for prog in data[:5]:
            bounties.append({
                "platform": "immunefi",
                "bounty_id": f"imm-{prog.get('id', prog.get('name', 'unknown'))}",
                "title": prog.get("name", "Untitled")[:200],
                "description": str(prog.get("description", ""))[:500],
                "payout_range": prog.get("maximum_reward", prog.get("maxBounty", "Unknown")),
                "repo_url": prog.get("url", prog.get("link", "")),
                "deadline": None,
                "bounty_type": "smart_contract_audit",
                "status": "open"
            })
    return bounties


async def scan_platforms() -> list:
    """Scan all bounty platforms and return combined results."""
    target = os.environ.get("TARGET_PLATFORM", "all").lower()
    all_bounties = []

    if target in ("all", "algora"):
        print(f"[{AGENT_NAME}] Scanning Algora...")
        all_bounties.extend(await scan_algora())

    if target in ("all", "github"):
        print(f"[{AGENT_NAME}] Scanning GitHub bounties...")
        token = os.environ.get("GITHUB_TOKEN", "")
        all_bounties.extend(await scan_github_bounties(token))

    if target in ("all", "immunefi"):
        print(f"[{AGENT_NAME}] Scanning Immunefi...")
        all_bounties.extend(await scan_immunefi())

    print(f"[{AGENT_NAME}] Total bounties discovered: {len(all_bounties)}")
    return all_bounties[:10]  # Top 10


async def run(comms, context: dict = None) -> dict:
    """Main agent function called by the Boss pipeline."""
    print(f"[{AGENT_NAME}] Phase 1: THE HUNT — Scanning bounty platforms...")
    bounties = await scan_platforms()

    result = {
        "agent": AGENT_NAME,
        "phase": "hunt",
        "bounties_found": len(bounties),
        "bounties": bounties,
        "timestamp": datetime.utcnow().isoformat()
    }

    if comms:
        await comms.save_state("bounty_discovered", json.dumps(result))
        await comms.save_pipeline_log("phase_1_hunt", f"Discovered {len(bounties)} bounties across platforms")

    return result


async def main():
    from core.bounty_comms import BountyComms
    comms = BountyComms(AGENT_ID, AGENT_NAME)
    await comms.startup()
    result = await run(comms)
    print(f"[{AGENT_NAME}] Results: {json.dumps(result, indent=2)[:1000]}")
    await comms.shutdown(f"Discovered {result['bounties_found']} bounties", "", "")

if __name__ == "__main__":
    asyncio.run(main())
