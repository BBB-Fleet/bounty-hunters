"""
BBB Fleet 2: Bounty Hunters — Agent 12: Evidence (Forensics Collector)
======================================================================
Phase 4/5 agent. Responsible for the unbroken cryptographic chain of custody.
Hashes the final artifacts (PoC, Diff, Logs), generates a unique Evidence Bundle ID,
and guarantees traceability for the final report.
"""

import asyncio
import json
import hashlib
import uuid
from datetime import datetime

AGENT_ID = 12
AGENT_NAME = "B2 Evidence"


def create_evidence_bundle(bounty_id: str, sandbox_id: str, target_commit: str, poc_code: str, patch_diff: str, execution_log: str) -> dict:
    """
    Creates a cryptographically sealed bundle containing all artifacts from a successful sandbox run.
    """
    bundle_id = f"EV-{datetime.utcnow().strftime('%Y%m%d')}-{uuid.uuid4().hex[:6].upper()}"
    
    # Concatenate all critical artifacts to form the hash payload
    raw_payload = f"{bounty_id}:{target_commit}:{sandbox_id}:{poc_code}:{patch_diff}:{execution_log}"
    
    # Generate the cryptographic signature of the artifacts
    sha256_hash = hashlib.sha256(raw_payload.encode('utf-8')).hexdigest()
    
    print(f"[{AGENT_NAME}] Created Evidence Bundle: {bundle_id}")
    print(f"[{AGENT_NAME}] Cryptographic Signature: {sha256_hash}")
    
    return {
        "bundle_id": bundle_id,
        "bounty_id": bounty_id,
        "target_commit": target_commit,
        "sandbox_id": sandbox_id,
        "artifacts": {
            "poc_code": poc_code,
            "patch_diff": patch_diff,
            "execution_log": execution_log
        },
        "sha256_hash": sha256_hash,
        "timestamp": datetime.utcnow().isoformat()
    }


async def run(comms, context: dict = None) -> dict:
    """Collect artifacts and generate the forensic bundle."""
    payload = context or {}
    print(f"[{AGENT_NAME}] Phase 4.5: EVIDENCE COLLECTION started...")
    
    bounty_id = payload.get("bounty_id", "UNKNOWN-BOUNTY")
    sandbox_id = payload.get("sandbox_id", "UNKNOWN-SANDBOX")
    target_commit = payload.get("target_commit", "UNKNOWN-COMMIT")
    poc_code = payload.get("poc_code", "")
    patch_diff = payload.get("patch_diff", "")
    execution_log = payload.get("execution_log", "")
    
    if not all([poc_code, execution_log]):
        print(f"[{AGENT_NAME}] WARNING: Missing critical artifacts (PoC or Logs).")
    
    evidence_bundle = create_evidence_bundle(
        bounty_id, sandbox_id, target_commit, poc_code, patch_diff, execution_log
    )
    
    result = {
        "agent": AGENT_NAME,
        "phase": "evidence_collection",
        "evidence_bundle": evidence_bundle,
        "timestamp": datetime.utcnow().isoformat()
    }

    if comms:
        await comms.save_pipeline_log("phase_4_evidence", f"Created Evidence Bundle {evidence_bundle['bundle_id']} ({evidence_bundle['sha256_hash'][:12]}...)")

    return result


async def main():
    from core.bounty_comms import BountyComms
    comms = BountyComms(AGENT_ID, AGENT_NAME)
    await comms.startup()
    
    mock_payload = {
        "bounty_id": "SHERLOCK-1002",
        "sandbox_id": "bbb_sandbox_20260806_abc123",
        "target_commit": "a1b2c3d4e5f67890",
        "poc_code": "def run_exploit():\n    pass",
        "patch_diff": "- old\n+ new",
        "execution_log": "Run 1: Success. Run 2: Success. Run 3: Success."
    }
    
    res = await run(comms, mock_payload)
    print(res)
    await comms.shutdown("Evidence collection complete", "", "")

if __name__ == "__main__":
    asyncio.run(main())
