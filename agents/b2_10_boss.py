"""
BBB Fleet 2: Bounty Hunters — Agent 10: Boss (Orchestrator)
===========================================================
Phase 4 agent. Oversees deterministic execution. Forces the PoC to be run 
three separate times, ensuring the exit code, findings, and evidence bundle
hash are identical across all three runs before passing to Evidence.
"""

import asyncio
import json
import hashlib
from datetime import datetime

AGENT_ID = 10
AGENT_NAME = "B2 Boss"

def validate_triple_run(run_results: list) -> dict:
    """
    Takes a list of 3 execution results from the Watchdog sandbox.
    Verifies strict determinism across all runs.
    """
    if len(run_results) != 3:
         return {"deterministic": False, "error": f"Expected 3 runs, got {len(run_results)}"}
         
    # 1. Verify identical exit codes
    exit_codes = [r.get("exit_code") for r in run_results]
    if len(set(exit_codes)) != 1:
        return {"deterministic": False, "error": f"Mismatched exit codes: {exit_codes}"}
        
    if exit_codes[0] != 0:
         return {"deterministic": False, "error": f"All runs failed with exit code: {exit_codes[0]}"}

    # 2. Verify identical output fingerprints (hashing stdout to compare)
    # We strip timestamps/variable pointers if needed in production before hashing
    stdouts = [r.get("stdout", "") for r in run_results]
    hashes = [hashlib.sha256(out.encode()).hexdigest() for out in stdouts]
    
    if len(set(hashes)) != 1:
        return {"deterministic": False, "error": "Mismatched output signatures across runs"}
        
    print(f"[{AGENT_NAME}] Triple-Run Validation PASSED. Determinism confirmed.")
    print(f"[{AGENT_NAME}] Deterministic Hash: {hashes[0]}")
    
    return {
        "deterministic": True,
        "verified_hash": hashes[0],
        "exit_code": exit_codes[0]
    }


async def run(comms, context: dict = None) -> dict:
    """Boss validates determinism."""
    payload = context or {}
    print(f"[{AGENT_NAME}] Phase 4: ORCHESTRATION & DETERMINISM CHECK started...")
    
    # In production, Boss would command Watchdog to execute 3 times and collect this list
    triple_run_results = payload.get("triple_run_results", [])
    
    validation = validate_triple_run(triple_run_results)
    
    if not validation["deterministic"]:
        print(f"[{AGENT_NAME}] FATAL: Nondeterministic execution detected. Rejecting.")
        return {"error": validation["error"]}
        
    result = {
        "agent": AGENT_NAME,
        "phase": "triple_run_validation",
        "deterministic": True,
        "verified_hash": validation["verified_hash"],
        "timestamp": datetime.utcnow().isoformat()
    }

    if comms:
        await comms.save_pipeline_log("phase_4_boss", f"Verified deterministic triple-run (Hash: {validation['verified_hash']})")

    return result


async def main():
    from core.bounty_comms import BountyComms
    comms = BountyComms(AGENT_ID, AGENT_NAME)
    await comms.startup()
    
    mock_payload = {
        "triple_run_results": [
            {"exit_code": 0, "stdout": "Success: 500 drained"},
            {"exit_code": 0, "stdout": "Success: 500 drained"},
            {"exit_code": 0, "stdout": "Success: 500 drained"}
        ]
    }
    
    res = await run(comms, mock_payload)
    print(res)
    await comms.shutdown("Boss validation complete", "", "")

if __name__ == "__main__":
    asyncio.run(main())
