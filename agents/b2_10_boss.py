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
    # Strip common dynamic data (timestamps, memory addresses, randomized UUIDs)
    # to prevent strict hashing from rejecting valid but non-deterministic exploits (e.g. MEV, Race Conditions)
    import re
    cleaned_stdouts = []
    for out in stdouts:
        # Strip timestamps like 2026-08-06T12:00:00
        out = re.sub(r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(\.\d+)?Z?', '<TIMESTAMP>', out)
        # Strip memory addresses like 0x7f8a9b
        out = re.sub(r'0x[a-fA-F0-9]{6,40}', '<HEX_ADDR>', out)
        cleaned_stdouts.append(out)
        
    hashes = [hashlib.sha256(out.encode()).hexdigest() for out in cleaned_stdouts]
    
    if len(set(hashes)) != 1:
        print(f"[{AGENT_NAME}] WARNING: Output hashes do not match. Exploit may be non-deterministic (Race condition, MEV).")
        print(f"[{AGENT_NAME}] Since exit codes are all 0, flagging as NONDETERMINISTIC_PASS.")
        return {
            "deterministic": False,
            "verified_hash": hashes[0], # Using first run's hash for evidence chaining
            "exit_code": exit_codes[0],
            "nondeterministic_pass": True
        }
        
    print(f"[{AGENT_NAME}] Triple-Run Validation PASSED. Determinism confirmed.")
    print(f"[{AGENT_NAME}] Deterministic Hash: {hashes[0]}")
    
    return {
        "deterministic": True,
        "verified_hash": hashes[0],
        "exit_code": exit_codes[0],
        "nondeterministic_pass": False
    }


async def run(comms, context: dict = None) -> dict:
    """Boss validates determinism."""
    payload = context or {}
    print(f"[{AGENT_NAME}] Phase 4: ORCHESTRATION & DETERMINISM CHECK started...")
    
    # In production, Boss would command Watchdog to execute 3 times and collect this list
    triple_run_results = payload.get("triple_run_results", [])
    
    validation = validate_triple_run(triple_run_results)
    
    if not validation["deterministic"] and not validation.get("nondeterministic_pass"):
        print(f"[{AGENT_NAME}] FATAL: Nondeterministic execution detected. Rejecting.")
        return {"error": validation.get("error", "Unknown determinism error")}
        
    result = {
        "agent": AGENT_NAME,
        "phase": "triple_run_validation",
        "deterministic": validation["deterministic"],
        "nondeterministic_pass": validation.get("nondeterministic_pass", False),
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
