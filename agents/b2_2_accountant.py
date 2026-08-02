"""
BBB Fleet 2: Bounty Hunters — Agent 2: Accountant (Bounty ROI Evaluator & Invoice Submitter)
=============================================================================================
Phase 2 & Phase 7 agent. Evaluates bounty compute ROI during approval, and submits
the final agreed submission to Fleet 1's handoff table.
"""

import asyncio
import json
from datetime import datetime

AGENT_ID = 2
AGENT_NAME = "B2 Accountant"


async def evaluate_bounty(bounty: dict) -> dict:
    """Evaluate compute cost vs estimated payout."""
    payout_str = str(bounty.get("payout_range", "0")).replace("$", "").replace(",", "")
    payout_val = 0.0
    try:
        # Try to parse numbers from string
        import re
        nums = re.findall(r"\d+\.?\d*", payout_str)
        if nums:
            payout_val = float(nums[-1])  # Take highest number found
    except Exception:
        payout_val = 50.0  # Default fallback assumption

    # Estimated Groq LLM API calls for full 7-phase run ~15-20 calls
    estimated_compute_cost = 0.05  # $0.05 equivalent compute time
    approved = payout_val >= 20.0 or payout_val == 0.0  # Accept if >= $20 or unknown

    return {
        "approved": approved,
        "estimated_payout": payout_val,
        "estimated_compute_cost": estimated_compute_cost,
        "roi_score": round(payout_val / max(estimated_compute_cost, 0.01), 2),
        "reason": f"Payout estimate ${payout_val} vs compute cost ${estimated_compute_cost}"
    }


async def submit_to_fleet1(comms, submission: dict) -> str:
    """Submit final verified bounty payload to Fleet 1's handoff table."""
    submission_id = f"BH-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
    handoff_payload = {
        "submission_id": submission_id,
        "bounty_platform": submission.get("platform", "algora"),
        "bounty_id": submission.get("bounty_id", "unknown"),
        "bounty_title": submission.get("bounty_title", "Untitled Bounty"),
        "bounty_url": submission.get("bounty_url", ""),
        "submission_payload": json.dumps(submission),
        "estimated_payout": submission.get("estimated_payout", 100.0),
        "requires_onchain": submission.get("requires_onchain", False),
        "gas_estimate_eth": submission.get("gas_estimate_eth", 0.0),
        "consensus_trials": submission.get("consensus_trials", 1),
        "status": "PENDING_FLEET1_REVIEW",
        "splits_vault": "0xc87c3e8CB21e5A630Baf8D38b2060aCBb047afCb"
    }

    if comms:
        await comms.save_to_handoff(handoff_payload)
        await comms.save_pipeline_log("phase_7_invoice", f"Submitted {submission_id} to Fleet 1 handoff")

    print(f"[{AGENT_NAME}] 🧾 INVOICE SUBMITTED TO FLEET 1: {submission_id}")
    return submission_id


async def run(comms, context: dict = None) -> dict:
    """Main agent function called by the Boss pipeline."""
    action = (context or {}).get("action", "evaluate")
    bounty = (context or {}).get("bounty", {})

    if action == "evaluate":
        res = await evaluate_bounty(bounty)
        res["agent"] = AGENT_NAME
        res["vote"] = "AGREE" if res["approved"] else "DISAGREE"
        if comms:
            await comms.save_state("bounty_evaluation", json.dumps(res))
        return res
    elif action == "submit":
        sub_id = await submit_to_fleet1(comms, bounty)
        return {"agent": AGENT_NAME, "submission_id": sub_id, "status": "submitted"}

    return {"agent": AGENT_NAME, "status": "idle"}


async def main():
    from core.bounty_comms import BountyComms
    comms = BountyComms(AGENT_ID, AGENT_NAME)
    await comms.startup()
    res = await run(comms, {"action": "evaluate", "bounty": {"payout_range": "$100"}})
    print(f"[{AGENT_NAME}] Result: {res}")
    await comms.shutdown("Evaluated test bounty", "", "")

if __name__ == "__main__":
    asyncio.run(main())
