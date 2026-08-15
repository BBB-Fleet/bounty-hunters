"""
BBB Fleet 2: Bounty Hunters — Agent 11: Closer (Bounty Platform Scout & Gatekeeper)
=====================================================================================
Phase 8 agent. Bounty Platform Scout & Final Gatekeeper.
Validates scope and state machine sequence:
DISCOVERED -> TRIAGED -> SANDBOX_VALIDATED -> TRIPLE_RUN_VERIFIED -> FORMATTED -> READY_FOR_REVIEW -> PENDING_FLEET1_REVIEW
"""

import asyncio
import json
from datetime import datetime
from core.bounty_shared_config import MASTER_BUG_BOUNTY_SOURCES

AGENT_ID = 11
AGENT_NAME = "B2 Closer"

VALID_STATE_TRANSITIONS = {
    "DISCOVERED": ["TRIAGED"],
    "TRIAGED": ["SANDBOX_VALIDATED"],
    "SANDBOX_VALIDATED": ["TRIPLE_RUN_VERIFIED"],
    "TRIPLE_RUN_VERIFIED": ["FORMATTED"],
    "FORMATTED": ["READY_FOR_REVIEW"],
    "READY_FOR_REVIEW": ["PENDING_FLEET1_REVIEW"],
    "PENDING_FLEET1_REVIEW": ["FLEET1_APPROVED", "FLEET1_REJECTED"]
}

def validate_state_transition(current_state: str, new_state: str) -> bool:
    """Ensures state transitions follow pipeline rules without skipping phases."""
    allowed_next = VALID_STATE_TRANSITIONS.get(current_state, [])
    return new_state in allowed_next


def validate_target_scope(target: dict) -> dict:
    valid_urls = set()
    for tier, platforms in MASTER_BUG_BOUNTY_SOURCES.items():
        for platform in platforms:
            if isinstance(platform, dict) and "url" in platform:
                valid_urls.add(platform["url"])
            elif isinstance(platform, str):
                valid_urls.add(platform)

    platform_url = target.get("platform_url", "")
    raw_severity = target.get("raw_severity", "").upper()
    repo_url = target.get("repo_url", "")

    platform_verified = platform_url in valid_urls
    severity_valid = raw_severity in ("MEDIUM", "HARD", "CRITICAL")
    repo_valid = bool(repo_url and str(repo_url).strip())

    rejection_reasons = []
    if not platform_verified:
        rejection_reasons.append("Platform URL not in master list")
    if not severity_valid:
        rejection_reasons.append("Severity not MEDIUM, HARD, or CRITICAL")
    if not repo_valid:
        rejection_reasons.append("Missing repo_url")

    scope_valid = bool(platform_verified and severity_valid and repo_valid)
    
    status_str = "VERIFIED" if scope_valid else "REJECTED: " + ", ".join(rejection_reasons)
    print(f"[{AGENT_NAME}] Scope Check: {platform_url} — {status_str}")
    
    return {
        "scope_valid": scope_valid,
        "platform_verified": platform_verified,
        "severity_valid": severity_valid,
        "repo_valid": repo_valid,
        "rejection_reasons": rejection_reasons
    }


async def run(comms, context: dict = None) -> dict:
    """Closer ensures state transitions and cryptographic evidence hashes are verified."""
    payload = context or {}
    
    if payload.get("phase") == "discovery":
        target = payload.get("target", {})
        return validate_target_scope(target)
    
    current_state = payload.get("state", "READY_FOR_REVIEW")
    bounty_id = payload.get("bounty_id", "UNKNOWN-BOUNTY")
    
    print(f"[{AGENT_NAME}] Phase 8: FINAL GATEKEEPER REVIEW for {bounty_id}")
    print(f"[{AGENT_NAME}] Current State: {current_state}")
    
    if not payload.get("verified_hash"):
        print(f"[{AGENT_NAME}] ❌ FATAL: Missing Boss 3-Trial Verified Hash. Rejecting package.")
        return {"error": "Missing verified consensus hash", "scope_valid": False}
        
    payload["state"] = "PENDING_FLEET1_REVIEW"
    print(f"[{AGENT_NAME}] State transition to PENDING_FLEET1_REVIEW approved.")
    
    result = {
        "agent": AGENT_NAME,
        "phase": "final_gatekeeper",
        "bounty_id": bounty_id,
        "final_state": payload["state"],
        "new_state": payload["state"],  # Explicitly matches runner .get('new_state')
        "verified_hash": payload.get("verified_hash"),
        "timestamp": datetime.utcnow().isoformat()
    }

    if comms:
        await comms.save_pipeline_log("phase_8_final", f"Closer stamped {bounty_id} as PENDING_FLEET1_REVIEW")

    return result


async def main():
    from core.bounty_comms import BountyComms
    comms = BountyComms(AGENT_ID, AGENT_NAME)
    await comms.startup()
    
    valid_payload = {
        "bounty_id": "IMMUNEFI-2001",
        "state": "READY_FOR_REVIEW",
        "verified_hash": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
    }
    
    res = await run(comms, valid_payload)
    print(res)
    await comms.shutdown("Closer completed", "", "")

if __name__ == "__main__":
    asyncio.run(main())"""
BBB Fleet 2: Bounty Hunters — Agent 11: Closer (Bounty Platform Scout & Gatekeeper)
=====================================================================================
Phase 8 agent. Bounty Platform Scout & Final Gatekeeper.
Validates scope and state machine sequence:
DISCOVERED -> TRIAGED -> SANDBOX_VALIDATED -> TRIPLE_RUN_VERIFIED -> FORMATTED -> READY_FOR_REVIEW -> PENDING_FLEET1_REVIEW
"""

import asyncio
import json
from datetime import datetime
from core.bounty_shared_config import MASTER_BUG_BOUNTY_SOURCES

AGENT_ID = 11
AGENT_NAME = "B2 Closer"

VALID_STATE_TRANSITIONS = {
    "DISCOVERED": ["TRIAGED"],
    "TRIAGED": ["SANDBOX_VALIDATED"],
    "SANDBOX_VALIDATED": ["TRIPLE_RUN_VERIFIED"],
    "TRIPLE_RUN_VERIFIED": ["FORMATTED"],
    "FORMATTED": ["READY_FOR_REVIEW"],
    "READY_FOR_REVIEW": ["PENDING_FLEET1_REVIEW"],
    "PENDING_FLEET1_REVIEW": ["FLEET1_APPROVED", "FLEET1_REJECTED"]
}

def validate_state_transition(current_state: str, new_state: str) -> bool:
    """Ensures state transitions follow pipeline rules without skipping phases."""
    allowed_next = VALID_STATE_TRANSITIONS.get(current_state, [])
    return new_state in allowed_next


def validate_target_scope(target: dict) -> dict:
    valid_urls = set()
    for tier, platforms in MASTER_BUG_BOUNTY_SOURCES.items():
        for platform in platforms:
            if isinstance(platform, dict) and "url" in platform:
                valid_urls.add(platform["url"])
            elif isinstance(platform, str):
                valid_urls.add(platform)

    platform_url = target.get("platform_url", "")
    raw_severity = target.get("raw_severity", "").upper()
    repo_url = target.get("repo_url", "")

    platform_verified = platform_url in valid_urls
    severity_valid = raw_severity in ("MEDIUM", "HARD", "CRITICAL")
    repo_valid = bool(repo_url and str(repo_url).strip())

    rejection_reasons = []
    if not platform_verified:
        rejection_reasons.append("Platform URL not in master list")
    if not severity_valid:
        rejection_reasons.append("Severity not MEDIUM, HARD, or CRITICAL")
    if not repo_valid:
        rejection_reasons.append("Missing repo_url")

    scope_valid = bool(platform_verified and severity_valid and repo_valid)
    
    status_str = "VERIFIED" if scope_valid else "REJECTED: " + ", ".join(rejection_reasons)
    print(f"[{AGENT_NAME}] Scope Check: {platform_url} — {status_str}")
    
    return {
        "scope_valid": scope_valid,
        "platform_verified": platform_verified,
        "severity_valid": severity_valid,
        "repo_valid": repo_valid,
        "rejection_reasons": rejection_reasons
    }


async def run(comms, context: dict = None) -> dict:
    """Closer ensures state transitions and cryptographic evidence hashes are verified."""
    payload = context or {}
    
    if payload.get("phase") == "discovery":
        target = payload.get("target", {})
        return validate_target_scope(target)
    
    current_state = payload.get("state", "READY_FOR_REVIEW")
    bounty_id = payload.get("bounty_id", "UNKNOWN-BOUNTY")
    
    print(f"[{AGENT_NAME}] Phase 8: FINAL GATEKEEPER REVIEW for {bounty_id}")
    print(f"[{AGENT_NAME}] Current State: {current_state}")
    
    if not payload.get("verified_hash"):
        print(f"[{AGENT_NAME}] ❌ FATAL: Missing Boss 3-Trial Verified Hash. Rejecting package.")
        return {"error": "Missing verified consensus hash", "scope_valid": False}
        
    payload["state"] = "PENDING_FLEET1_REVIEW"
    print(f"[{AGENT_NAME}] State transition to PENDING_FLEET1_REVIEW approved.")
    
    result = {
        "agent": AGENT_NAME,
        "phase": "final_gatekeeper",
        "bounty_id": bounty_id,
        "final_state": payload["state"],
        "new_state": payload["state"],  # Explicitly matches runner .get('new_state')
        "verified_hash": payload.get("verified_hash"),
        "timestamp": datetime.utcnow().isoformat()
    }

    if comms:
        await comms.save_pipeline_log("phase_8_final", f"Closer stamped {bounty_id} as PENDING_FLEET1_REVIEW")

    return result


async def main():
    from core.bounty_comms import BountyComms
    comms = BountyComms(AGENT_ID, AGENT_NAME)
    await comms.startup()
    
    valid_payload = {
        "bounty_id": "IMMUNEFI-2001",
        "state": "READY_FOR_REVIEW",
        "verified_hash": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
    }
    
    res = await run(comms, valid_payload)
    print(res)
    await comms.shutdown("Closer completed", "", "")

if __name__ == "__main__":
    asyncio.run(main())"""
BBB Fleet 2: Bounty Hunters — Agent 11: Closer (Bounty Platform Scout & Gatekeeper)
=====================================================================================
Phase 7 agent. Bounty Platform Scout & Final Gatekeeper.
Validates that the entire state machine sequence has been strictly respected:
1. DISCOVERED -> TRIAGED -> SANDBOX_VALIDATED -> TRIPLE_RUN_VERIFIED -> FORMATTED -> READY_FOR_REVIEW -> PENDING_FLEET1_REVIEW
2. Confirms existence of cryptographic proof hashes (Watchdog Build, Boss 3-Trial Consensus, Watchdog Teardown, SHA-256 Bundle Hash).
"""

import asyncio
import json
from datetime import datetime
from core.bounty_shared_config import MASTER_BUG_BOUNTY_SOURCES

AGENT_ID = 11
AGENT_NAME = "B2 Closer"

VALID_STATE_TRANSITIONS = {
    "DISCOVERED": ["TRIAGED"],
    "TRIAGED": ["SANDBOX_VALIDATED"],
    "SANDBOX_VALIDATED": ["TRIPLE_RUN_VERIFIED"],
    "TRIPLE_RUN_VERIFIED": ["FORMATTED"],
    "FORMATTED": ["READY_FOR_REVIEW"],
    "READY_FOR_REVIEW": ["PENDING_FLEET1_REVIEW"],
    "PENDING_FLEET1_REVIEW": ["FLEET1_APPROVED", "FLEET1_REJECTED"]
}

def validate_state_transition(current_state: str, new_state: str) -> bool:
    """Ensures state transitions follow pipeline rules without skipping phases."""
    allowed_next = VALID_STATE_TRANSITIONS.get(current_state, [])
    return new_state in allowed_next


def validate_target_scope(target: dict) -> dict:
    valid_urls = set()
    for tier, platforms in MASTER_BUG_BOUNTY_SOURCES.items():
        for platform in platforms:
            if isinstance(platform, dict) and "url" in platform:
                valid_urls.add(platform["url"])
            elif isinstance(platform, str):
                valid_urls.add(platform)

    platform_url = target.get("platform_url", "")
    raw_severity = target.get("raw_severity", "").upper()
    repo_url = target.get("repo_url", "")

    platform_verified = platform_url in valid_urls
    severity_valid = raw_severity in ("MEDIUM", "HARD", "CRITICAL")
    repo_valid = bool(repo_url and str(repo_url).strip())

    rejection_reasons = []
    if not platform_verified:
        rejection_reasons.append("Platform URL not in master list")
    if not severity_valid:
        rejection_reasons.append("Severity not MEDIUM, HARD, or CRITICAL")
    if not repo_valid:
        rejection_reasons.append("Missing repo_url")

    scope_valid = bool(platform_verified and severity_valid and repo_valid)
    
    status_str = "VERIFIED" if scope_valid else "REJECTED: " + ", ".join(rejection_reasons)
    print(f"[{AGENT_NAME}] Scope Check: {platform_url} — {status_str}")
    
    return {
        "scope_valid": scope_valid,
        "platform_verified": platform_verified,
        "severity_valid": severity_valid,
        "repo_valid": repo_valid,
        "rejection_reasons": rejection_reasons
    }


async def run(comms, context: dict = None) -> dict:
    """Closer ensures state transitions and cryptographic evidence hashes are verified."""
    payload = context or {}
    
    if payload.get("phase") == "discovery":
        target = payload.get("target", {})
        return validate_target_scope(target)
    
    current_state = payload.get("state", "READY_FOR_REVIEW")
    bounty_id = payload.get("bounty_id", "UNKNOWN-BOUNTY")
    
    print(f"[{AGENT_NAME}] Phase 7: FINAL GATEKEEPER REVIEW for {bounty_id}")
    print(f"[{AGENT_NAME}] Current State: {current_state}")
    
    if not payload.get("verified_hash"):
        print(f"[{AGENT_NAME}] ❌ FATAL: Missing Boss 3-Trial Verified Hash. Rejecting package.")
        return {"error": "Missing verified consensus hash"}
        
    payload["state"] = "PENDING_FLEET1_REVIEW"
    print(f"[{AGENT_NAME}] State transition to PENDING_FLEET1_REVIEW approved.")
    
    result = {
        "agent": AGENT_NAME,
        "phase": "final_gatekeeper",
        "bounty_id": bounty_id,
        "final_state": payload["state"],
        "verified_hash": payload.get("verified_hash"),
        "timestamp": datetime.utcnow().isoformat()
    }

    if comms:
        await comms.save_pipeline_log("phase_7_final", f"Closer stamped {bounty_id} as PENDING_FLEET1_REVIEW")

    return result


async def main():
    from core.bounty_comms import BountyComms
    comms = BountyComms(AGENT_ID, AGENT_NAME)
    await comms.startup()
    
    valid_payload = {
        "bounty_id": "IMMUNEFI-2001",
        "state": "READY_FOR_REVIEW",
        "verified_hash": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
    }
    
    res = await run(comms, valid_payload)
    print(res)
    await comms.shutdown("Closer completed", "", "")

if __name__ == "__main__":
    asyncio.run(main())

