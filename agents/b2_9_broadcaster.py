"""
BBB Fleet 2: Bounty Hunters — Agent 9: Broadcaster (Submission Formatter)
==========================================================================
Phase 6 agent. Formats agreed solution drafts into clean, platform-specific
submission payloads (GitHub PR, Sherlock Issue, Immunefi Report).
"""

import asyncio
import json
from datetime import datetime

AGENT_ID = 9
AGENT_NAME = "B2 Broadcaster"


async def run(comms, context: dict = None) -> dict:
    """Format agreed draft into platform-specific submission markdown."""
    payload = context or {}
    platform = payload.get("platform", "algora").lower()
    print(f"[{AGENT_NAME}] Phase 6: PACKAGING submission for platform: {platform}...")

    from core.llm_client import query_llm

    format_style = {
        "algora": "GitHub Pull Request description with summary, fix details, and test results",
        "github": "GitHub Pull Request description referencing issue ID",
        "sherlock": "Sherlock GitHub Issue format (Title, Severity, Impact, Vulnerability Detail, PoC, Recommendation)",
        "immunefi": "Immunefi Bug Report format (Title, Asset, Bug Type, Impact, Steps to Reproduce, PoC Script, Recommendation)"
    }.get(platform, "Standard Technical Bug Report")

    prompt = (
        f"You are {AGENT_NAME}, lead technical writer and submission formatter for the BBB mercenary fleet.\n"
        f"Format this agreed technical draft into a professional submission using {format_style}:\n\n"
        f"Bounty Title: {payload.get('bounty_title', '')}\n"
        f"Draft Solution:\n{payload.get('draft', '')[:1200]}\n"
        f"Watchdog Audit:\n{payload.get('audit', '')[:500]}\n\n"
        f"Produce the complete, perfectly formatted Markdown submission payload."
    )
    formatted_body = await query_llm(prompt) or "Formatted Bounty Submission Payload."

    result = {
        "agent": AGENT_NAME,
        "phase": "packaging",
        "platform": platform,
        "formatted_submission": formatted_body,
        "submission_type": "PR" if platform in ("algora", "github") else "REPORT",
        "bounty_title": payload.get("bounty_title", ""),
        "bounty_id": payload.get("bounty_id", ""),
        "estimated_payout": payload.get("estimated_payout", 100.0),
        "requires_onchain": payload.get("requires_onchain", False),
        "gas_estimate_eth": payload.get("gas_estimate_eth", 0.0),
        "consensus_trials": payload.get("consensus_trials", 1),
        "timestamp": datetime.utcnow().isoformat()
    }

    if comms:
        await comms.save_state("bounty_final_submission", json.dumps(result))
        await comms.save_pipeline_log("phase_6_packaging", f"Formatted final submission for {platform}")

    print(f"[{AGENT_NAME}] Packaging complete ({len(formatted_body)} chars)")
    return result


async def main():
    from core.bounty_comms import BountyComms
    comms = BountyComms(AGENT_ID, AGENT_NAME)
    await comms.startup()
    res = await run(comms, {"platform": "algora", "bounty_title": "Test Bounty", "draft": "Fix applied to repo."})
    print(f"[{AGENT_NAME}] Result:\n{res['formatted_submission'][:500]}")
    await comms.shutdown("Packaging completed", "", "")

if __name__ == "__main__":
    asyncio.run(main())
