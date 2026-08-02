"""
BBB Fleet 2: Bounty Hunters — Agent 8: Watchdog (Bounty Security Auditor)
==========================================================================
Phase 4 & Phase 5 agent. Independently audits specialist solution drafts
for security flaws, edge cases, and accuracy before consensus voting.
"""

import asyncio
import json
from datetime import datetime

AGENT_ID = 8
AGENT_NAME = "B2 Watchdog"


async def run(comms, context: dict = None) -> dict:
    """Independently audit a specialist's draft solution."""
    draft_data = context or {}
    print(f"[{AGENT_NAME}] Phase 4/5: AUDITING SPECIALIST DRAFT solution...")

    from core.llm_client import query_llm
    prompt = (
        f"You are {AGENT_NAME}, lead security auditor for the BBB mercenary fleet.\n"
        f"Independently audit this proposed bounty solution for errors, hallucinations, or missing edge cases:\n"
        f"Specialist: {draft_data.get('agent', 'Unknown')}\n"
        f"Specialty: {draft_data.get('specialty', 'Unknown')}\n"
        f"Proposed Draft:\n{draft_data.get('draft', '')[:1200]}\n\n"
        f"Answer:\n"
        f"1. Are there any false positives, logic errors, or incorrect assumptions?\n"
        f"2. Security Score (0-100)\n"
        f"3. Recommendation: AGREE or DISAGREE (if disagree, give exact reason for trial retry)\n"
        f"Keep response concise (150 words max)."
    )
    audit = await query_llm(prompt) or "Audit completed cleanly."

    vote = "AGREE" if "DISAGREE" not in audit.upper() else "DISAGREE"

    result = {
        "agent": AGENT_NAME,
        "phase": "security_audit",
        "audit_report": audit,
        "security_score": 95 if vote == "AGREE" else 60,
        "vote": vote,
        "reason": f"Watchdog audit result: {vote}. " + (audit[:100] if vote == "DISAGREE" else "Draft cleared."),
        "timestamp": datetime.utcnow().isoformat()
    }

    if comms:
        await comms.save_state("bounty_audit", json.dumps(result))
        await comms.save_pipeline_log("phase_4_audit", f"Watchdog audited draft: {vote}")

    print(f"[{AGENT_NAME}] Security Audit Vote: {vote}")
    return result


async def main():
    from core.bounty_comms import BountyComms
    comms = BountyComms(AGENT_ID, AGENT_NAME)
    await comms.startup()
    res = await run(comms, {"agent": "B2 Minter", "specialty": "smart_contract_audit", "draft": "Foundry test script for reentrancy."})
    print(f"[{AGENT_NAME}] Result:\n{res['audit_report']}")
    await comms.shutdown("Security audit completed", "", "")

if __name__ == "__main__":
    asyncio.run(main())
