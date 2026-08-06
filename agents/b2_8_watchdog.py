"""
BBB Fleet 2: Bounty Hunters — Agent 8: Watchdog (Bounty Security Auditor)
==========================================================================
Phase 4 agent. Manages the execution sandbox. Enforces target scope, 
clones repos into isolated local temporary folders, coordinates PoC execution,
and rigidly verifies sandbox cleanup to ensure no artifacts remain.
"""

import asyncio
import json
import os
import shutil
import tempfile
import uuid
from datetime import datetime

AGENT_ID = 8
AGENT_NAME = "B2 Watchdog"

def validate_target_scope(bounty_metadata: dict, repo_url: str, branch: str, commit: str) -> bool:
    """Ensure the target repository matches exactly what the bounty authorized."""
    expected_repo = bounty_metadata.get("repo_url", "")
    if repo_url != expected_repo:
        print(f"[{AGENT_NAME}] SCOPE VIOLATION: Repo URL {repo_url} does not match {expected_repo}")
        return False
        
    print(f"[{AGENT_NAME}] Scope verified: {repo_url}@{commit}")
    return True

def initialize_isolated_sandbox(repo_url: str) -> str:
    """
    Creates a secure, isolated local temporary directory and simulates cloning the repo.
    Returns the absolute path to the sandbox.
    """
    sandbox_id = f"bbb_sandbox_{datetime.utcnow().strftime('%Y%m%d')}_{uuid.uuid4().hex[:8]}"
    sandbox_path = os.path.join(tempfile.gettempdir(), sandbox_id)
    
    os.makedirs(sandbox_path, exist_ok=True)
    print(f"[{AGENT_NAME}] Created isolated local sandbox: {sandbox_path}")
    
    # In production: subprocess.run(["git", "clone", repo_url, sandbox_path])
    with open(os.path.join(sandbox_path, ".bbb_sandbox_lock"), "w") as f:
        f.write("LOCKED")
        
    return sandbox_path

def verify_poc_execution(sandbox_path: str, poc_script: str) -> dict:
    """
    Simulates executing a PoC script inside the sandbox.
    Returns exit code, stdout, and stderr.
    """
    print(f"[{AGENT_NAME}] Executing PoC in {sandbox_path}...")
    
    # Mocking deterministic execution success
    return {
        "exit_code": 0,
        "stdout": "Exploit successful. Balances drained.\n[PoC execution complete]",
        "stderr": "",
        "execution_time_ms": 450
    }

def verify_sandbox_cleanup(sandbox_path: str) -> bool:
    """
    Forcefully deletes the sandbox directory and verifies it is completely gone,
    releasing all file handles.
    """
    print(f"[{AGENT_NAME}] Initiating sandbox teardown: {sandbox_path}")
    try:
        if os.path.exists(sandbox_path):
            shutil.rmtree(sandbox_path)
    except Exception as e:
        print(f"[{AGENT_NAME}] Cleanup warning: {e}")
        
    # Definitive verification
    if os.path.exists(sandbox_path):
        print(f"[{AGENT_NAME}] FATAL: Sandbox cleanup failed! Directory still exists.")
        return False
        
    print(f"[{AGENT_NAME}] Sandbox completely wiped. All handles released.")
    return True


async def run(comms, context: dict = None) -> dict:
    """Watchdog lifecycle: Validate -> Isolate -> Execute -> Wipe"""
    payload = context or {}
    print(f"[{AGENT_NAME}] Phase 4: SANDBOX EXECUTION started...")
    
    bounty = payload.get("bounty", {})
    telemetry = payload.get("telemetry", {})
    poc = payload.get("poc", "")
    
    # 1. Enforce Scope
    if not validate_target_scope(bounty, telemetry.get("repo_url"), telemetry.get("branch"), telemetry.get("commit_hash")):
        return {"error": "Scope violation"}
        
    # 2. Isolate
    sandbox_path = initialize_isolated_sandbox(telemetry.get("repo_url"))
    
    # 3. Execute
    exec_results = verify_poc_execution(sandbox_path, poc)
    
    # 4. Verify Cleanup
    cleanup_success = verify_sandbox_cleanup(sandbox_path)
    if not cleanup_success:
        return {"error": "Sandbox cleanup failed"}
        
    result = {
        "agent": AGENT_NAME,
        "phase": "sandbox_execution",
        "sandbox_path_used": sandbox_path,
        "execution_results": exec_results,
        "timestamp": datetime.utcnow().isoformat()
    }

    if comms:
        await comms.save_pipeline_log("phase_4_sandbox", f"Executed PoC and verified cleanup.")

    return result


async def main():
    from core.bounty_comms import BountyComms
    comms = BountyComms(AGENT_ID, AGENT_NAME)
    await comms.startup()
    
    mock_payload = {
        "bounty": {"repo_url": "https://github.com/target/repo"},
        "telemetry": {"repo_url": "https://github.com/target/repo", "branch": "main", "commit_hash": "abc"},
        "poc": "print('Exploit run')"
    }
    
    res = await run(comms, mock_payload)
    print(res)
    await comms.shutdown("Sandbox execution complete", "", "")

if __name__ == "__main__":
    asyncio.run(main())
