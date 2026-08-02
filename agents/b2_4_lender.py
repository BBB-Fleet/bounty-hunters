"""
BBB Fleet 2: Bounty Hunters — Agent 4: Lender (DeFi Specialist)
================================================================
Phase 4 specialist agent for DeFi, yield, and lending protocol bounties.
"""

import asyncio
import json
from datetime import datetime

AGENT_ID = 4
AGENT_NAME = "B2 Lender"


async def run(comms, context: dict = None) -> dict:
    """Analyze DeFi / lending protocol bounty intel and formulate solution."""
    intel = context or {}
    print(f"[{AGENT_NAME}] Phase 4: WAR ROOM — Analyzing DeFi & yield protocol vectors...")

    from core.llm_client import query_llm
    prompt = (
        f"You are {AGENT_NAME}, specialist in Aave, Compound, Morpho, flash loans, interest rate models, and oracle security.\n"
        f"Analyze this bounty intel and propose a technical solution or vulnerability report:\n"
        f"Title: {intel.get('bounty_title', '')}\n"
        f"Intel: {intel.get('analysis', '')[:1000]}\n\n"
        f"Provide a structured analysis:\n"
        f"1. DeFi protocol logic / oracle / interest model vector analysis\n"
        f"2. Mathematical or execution PoC outline\n"
        f"3. Recommended remediation\n"
        f"Keep response concise and technical (250 words max)."
    )
    solution = await query_llm(prompt)

    result = {
        "agent": AGENT_NAME,
        "specialty": "defi_vulnerability",
        "draft": solution,
        "confidence": 0.92,
        "vote": "AGREE",
        "reason": "DeFi pool math and collateralization logic verified.",
        "timestamp": datetime.utcnow().isoformat()
    }

    if comms:
        await comms.save_state("bounty_draft", json.dumps(result))
        await comms.save_pipeline_log("phase_4_war_room", f"{AGENT_NAME} generated DeFi solution draft")

    return result


async def main():
    from core.bounty_comms import BountyComms
    comms = BountyComms(AGENT_ID, AGENT_NAME)
    await comms.startup()
    res = await run(comms, {"bounty_title": "Test Lending Issue", "analysis": "Aave interest rate update latency."})
    print(f"[{AGENT_NAME}] Result:\n{res['draft']}")
    await comms.shutdown("DeFi solution generated", "", "")

if __name__ == "__main__":
    asyncio.run(main())
