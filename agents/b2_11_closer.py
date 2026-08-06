"""
BBB Fleet 2: Bounty Hunters — Agent 11: Closer (Deal Sealer)
============================================================
Phase 7 agent. The final gatekeeper. Validates the entire state machine 
has been respected before stamping PENDING_FLEET1_REVIEW and committing 
the final bundle to the Neon database.
"""

import asyncio
import json
from datetime import datetime

AGENT_ID = 11
AGENT_NAME = "B2 Closer"

# Strict State Machine Transition Rules
VALID_STATE_TRANSITIONS = {
    "DISCOVERED": ["TRIAGED"],
    "TRIAGED": ["SANDBOX_VALIDATED"],
    "SANDBOX_VALIDATED": ["TRIPLE_RUN_VERIFIED"],
    "TRIPLE_RUN_VERIFIED": ["READY_FOR_REVIEW"],
    "READY_FOR_REVIEW": ["PENDING_FLEET1_REVIEW"],
    "PENDING_FLEET1_REVIEW": ["FLEET1_APPROVED", "FLEET1_REJECTED"]
}

def validate_state_transition(current_state: str, new_state: str) -> bool:
    """Ensures we don't skip phases in the state machine."""
    allowed_next = VALID_STATE_TRANSITIONS.get(current_state, [])
    return new_state in allowed_next


async def commit_to_neon_db(payload: dict) -> bool:
    """
    Mock function to represent the final insertion into the Neon Postgres database.
    In production, this executes the actual SQL INSERT into `bbb_fleet_handoff`.
    """
    print(f"[{AGENT_NAME}] Preparing DB commit for: {payload.get('bounty_id')}")
    print(f"[{AGENT_NAME}] Evidence Bundle Hash: {payload.get('evidence_hash')}")
    # Simulating DB latency
    await asyncio.sleep(1)
    print(f"[{AGENT_NAME}] Successfully committed to Neon DB table `bbb_fleet_handoff`.")
    return True


async def run(comms, context: dict = None) -> dict:
    """Closer ensures all requirements are met before sending to Fleet 1."""
    payload = context or {}
    
    current_state = payload.get("state", "UNKNOWN")
    bounty_id = payload.get("bounty_id", "Unknown")
    
    print(f"[{AGENT_NAME}] Phase 7: FINAL PACKAGE REVIEW for {bounty_id}")
    print(f"[{AGENT_NAME}] Current State: {current_state}")
    
    # 1. Validate State Machine
    if current_state != "READY_FOR_REVIEW":
        print(f"[{AGENT_NAME}] FATAL: Package {bounty_id} is in state {current_state}. Must be READY_FOR_REVIEW.")
        return {"error": "Invalid state", "state": current_state}
        
    # 2. Check for missing critical data
    if not payload.get("evidence_hash"):
        print(f"[{AGENT_NAME}] FATAL: Missing Evidence Hash. Cannot commit.")
        return {"error": "Missing evidence hash"}
        
    # 3. Transition State
    if not validate_state_transition(current_state, "PENDING_FLEET1_REVIEW"):
         print(f"[{AGENT_NAME}] FATAL: Invalid state transition.")
         return {"error": "Invalid state transition"}
         
    payload["state"] = "PENDING_FLEET1_REVIEW"
    print(f"[{AGENT_NAME}] State transition to PENDING_FLEET1_REVIEW approved.")
    
    # 4. Commit to Database
    success = await commit_to_neon_db(payload)
    
    result = {
        "agent": AGENT_NAME,
        "phase": "final_signoff",
        "bounty_id": bounty_id,
        "final_state": payload["state"],
        "db_committed": success,
        "timestamp": datetime.utcnow().isoformat()
    }

    if comms and success:
        await comms.save_pipeline_log("phase_7_final", f"Closer stamped {bounty_id} as PENDING_FLEET1_REVIEW")

    return result


async def main():
    from core.bounty_comms import BountyComms
    comms = BountyComms(AGENT_ID, AGENT_NAME)
    await comms.startup()
    
    # Mock valid payload
    valid_payload = {
        "bounty_id": "SHERLOCK-1002",
        "state": "READY_FOR_REVIEW",
        "evidence_hash": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
    }
    
    await run(comms, valid_payload)
    await comms.shutdown("Closer completed", "", "")

if __name__ == "__main__":
    asyncio.run(main())
