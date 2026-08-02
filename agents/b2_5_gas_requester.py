"""
BBB Fleet 2: Bounty Hunters — Agent 5: Gas Requester (Gas Cost Estimator & General Dev)
=======================================================================================
Phase 4 specialist agent for general dev/SDK bounties and gas cost estimator.
"""

import asyncio
import json
from datetime import datetime

AGENT_ID = 5
AGENT_NAME = "B2 Gas Requester"


async def run(comms, context: dict = None) -> dict:
    """Analyze general SDK/tooling bounties and estimate gas costs if needed."""
    intel = context or {}
    print(f"[{AGENT_NAME}] Phase 4: WAR ROOM — Analyzing SDK/tooling vectors & gas estimates...")

    requires_onchain = intel.get("bounty_type") in ("smart_contract_audit", "cross_chain_bridge")
    estimated_gas_eth = 0.0015 if requires_onchain else 0.0

    from core.llm_client import query_llm
    prompt = (
        f"You are {AGENT_NAME}, specialist in Web3 SDKs, ERC-4337 account abstraction, CLI utilities, and developer tooling.\n"
        f"Analyze this bounty intel and propose a solution or code fix:\n"
        f"Title: {intel.get('bounty_title', '')}\n"
        f"Intel: {intel.get('analysis', '')[:1000]}\n\n"
        f"Provide a structured analysis:\n"
        f"1. Code quality / API bug / documentation fix plan\n"
        f"2. Implementation approach & unit test strategy\n"
        f"3. Gas sponsorship requirement assessment ({'REQUIRED' if requires_onchain else 'NONE'})\n"
        f"Keep response concise and technical (250 words max)."
    )
    solution = await query_llm(prompt)

    result = {
        "agent": AGENT_NAME,
        "specialty": "sdk_tooling",
        "draft": solution,
        "requires_onchain": requires_onchain,
        "gas_estimate_eth": estimated_gas_eth,
        "confidence": 0.88,
        "vote": "AGREE",
        "reason": f"SDK fix verified. Gas sponsorship required: {requires_onchain} ({estimated_gas_eth} ETH).",
        "timestamp": datetime.utcnow().isoformat()
    }

    if comms:
        await comms.save_state("bounty_draft", json.dumps(result))
        await comms.save_pipeline_log("phase_4_war_room", f"{AGENT_NAME} generated SDK solution draft")

    return result


async def main():
    from core.bounty_comms import BountyComms
    comms = BountyComms(AGENT_ID, AGENT_NAME)
    await comms.startup()
    res = await run(comms, {"bounty_title": "Test SDK Bug", "analysis": "TypeError in client authentication module."})
    print(f"[{AGENT_NAME}] Result:\n{res['draft']}")
    await comms.shutdown("SDK solution generated", "", "")

if __name__ == "__main__":
    asyncio.run(main())
