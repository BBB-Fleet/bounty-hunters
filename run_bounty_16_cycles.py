"""
BBB Fleet 2: Bounty Hunters — 16-Cycle Bounty Pipeline Runner
=============================================================
Orchestrates full Fleet 2 pipeline:

Phase 1: Scanner (Agent 1)
Phase 2: Accountant (Agent 2)
Phase 3: Specialist (Agents 3–7: Bridge / Lender / Gas / Solana / Minter)
Phase 4: Watchdog (Agent 8)
Phase 5: Boss (Agent 10)
Phase 6: Broadcaster (Agent 9)
Phase 7: Evidence (Agent 12)
Phase 8: Closer (Agent 11)
Neon DB Handoff: BountyComms.save_to_handoff
"""

import asyncio
import json
import os
from datetime import datetime, timezone

# ─── Agent Imports (ALL 12 Agents) ──────────────────────────────────────
from agents.b2_1_scanner import run as run_b2_scanner           # Agent 1:  Scanner
from agents.b2_2_accountant import run as run_b2_accountant     # Agent 2:  Accountant
from agents.b2_3_bridge import run as run_b2_bridge             # Agent 3:  Bridge Specialist
from agents.b2_4_lender import run as run_b2_lender             # Agent 4:  Lender Specialist
from agents.b2_5_gas_requester import run as run_b2_gas         # Agent 5:  Gas Requester
from agents.b2_6_solana_ghost import run as run_b2_solana       # Agent 6:  Solana Ghost
from agents.b2_7_minter import run as run_b2_minter             # Agent 7:  Minter Specialist
from agents.b2_8_watchdog import run as run_b2_watchdog         # Agent 8:  Watchdog
from agents.b2_9_broadcaster import run as run_b2_broadcaster   # Agent 9:  Broadcaster
from agents.b2_10_boss import run as run_b2_boss                # Agent 10: Boss
from agents.b2_11_closer import run as run_b2_closer            # Agent 11: Closer
from agents.b2_12_evidence import run as run_b2_evidence        # Agent 12: Evidence

from core.bounty_comms import BountyComms


TARGET_PLATFORM = os.getenv("TARGET_PLATFORM", "all").lower()
MAX_CYCLES = 16


# ─── Helper: Select Specialist Based on Bounty ──────────────────────────

def select_specialist_agent(bounty: dict):
    """
    Chooses the correct specialist agent based on bounty title / vulnerability type.
    Returns (agent_name, agent_run_fn).
    """
    title = (bounty.get("bounty_title") or bounty.get("title") or "").lower()
    vuln_type = (bounty.get("vulnerability_type") or "").lower()

    text = f"{title} {vuln_type}"

    if any(k in text for k in ["bridge", "cross-chain", "cross chain"]):
        return "bridge", run_b2_bridge

    if any(k in text for k in ["lending", "oracle", "defi", "liquidation", "price"]):
        return "lender", run_b2_lender

    if any(k in text for k in ["permit2", "permit 2", "router", "allowance", "universal router"]):
        return "minter", run_b2_minter

    if any(k in text for k in ["gas", "dos", "loop", "out-of-gas", "out of gas"]):
        return "gas", run_b2_gas

    # Default: Solana Ghost pre-check
    return "solana", run_b2_solana


# ─── Helper: Normalize Scanner Output ───────────────────────────────────

def normalize_scanner_output(scanner_result: dict) -> list[dict]:
    """
    Takes Agent 1 (Scanner) output and returns a list of bounty dicts
    in a unified schema for downstream agents.
    """
    if not scanner_result:
        return []

    bounties = scanner_result.get("bounties") or scanner_result.get("results") or []
    if isinstance(bounties, dict):
        bounties = [bounties]

    normalized = []
    for b in bounties:
        if not isinstance(b, dict):
            continue
        # Ensure core fields exist
        norm = {
            "bounty_id": b.get("bounty_id") or b.get("id") or f"UNKNOWN-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}",
            "bounty_title": b.get("bounty_title") or b.get("title") or "Untitled Bounty",
            "bounty_platform": b.get("platform") or b.get("source") or TARGET_PLATFORM,
            "platform_url": b.get("platform_url") or b.get("url") or "",
            "repo_url": b.get("repo_url") or b.get("target_repo") or "",
            "severity": b.get("severity") or "CRITICAL",
            "vulnerability_type": b.get("vulnerability_type") or "smart_contract_audit",
            "estimated_payout": b.get("estimated_payout") or b.get("bounty_size_usd") or 0.0,
            "raw": b,
        }
        normalized.append(norm)

    return normalized


# ─── Main Pipeline for a Single Bounty ──────────────────────────────────

async def process_single_bounty(comms: BountyComms, bounty: dict, cycle_index: int) -> None:
    """
    Runs full Fleet 2 pipeline for a single bounty:
    Scanner -> Accountant -> Specialist -> Watchdog -> Evidence -> Boss -> Broadcaster -> Closer -> Neon handoff
    """
    bounty_id = bounty.get("bounty_id")
    bounty_title = bounty.get("bounty_title")
    platform = bounty.get("bounty_platform")

    print(f"[PIPELINE] Cycle {cycle_index} :: Processing bounty {bounty_id} :: {bounty_title} :: {platform}")

    # Phase 2: Accountant (risk / payout normalization)
    accountant_payload = {
        "bounty": bounty,
        "telemetry": {
            "platform": platform,
            "repo_url": bounty.get("repo_url"),
        },
    }
    accountant_res = await run_b2_accountant(comms, accountant_payload)

    # Phase 3: Specialist selection + run
    specialist_name, specialist_run = select_specialist_agent(bounty)
    specialist_payload = {
        "bounty_title": bounty_title,
        "repo_url": bounty.get("repo_url"),
        "vulnerability_type": bounty.get("vulnerability_type"),
        "bounty": bounty,
        "accountant": accountant_res,
    }
    specialist_res = await specialist_run(comms, specialist_payload)

    # Phase 4: Watchdog sandbox execution of PoC
    poc_code = specialist_res.get("poc_code") or specialist_res.get("poc") or ""
    watchdog_payload = {
        "bounty": bounty,
        "poc": poc_code,
        "telemetry": {
            "repo_url": bounty.get("repo_url"),
        },
    }
    watchdog_res = await run_b2_watchdog(comms, watchdog_payload)

    # Phase 5: Evidence bundling
    evidence_payload = {
        "bounty": bounty,
        "accountant": accountant_res,
        "specialist": specialist_res,
        "watchdog": watchdog_res,
    }
    evidence_res = await run_b2_evidence(comms, evidence_payload)

    # Phase 6: Boss consensus
    boss_payload = {
        "bounty": bounty,
        "accountant": accountant_res,
        "specialist": specialist_res,
        "watchdog": watchdog_res,
        "evidence": evidence_res,
    }
    boss_res = await run_b2_boss(comms, boss_payload)

    # Phase 7: Broadcaster (platform-specific markdown)
    broadcaster_payload = {
        "bounty_id": bounty_id,
        "bounty_title": bounty_title,
        "platform": platform,
        "severity": bounty.get("severity"),
        "estimated_payout": bounty.get("estimated_payout"),
        "repo_url": bounty.get("repo_url"),
        "draft": specialist_res.get("draft") or boss_res.get("vulnerability_draft"),
        "poc_code": poc_code,
        "evidence": evidence_res,
        "sandbox_build_hash": watchdog_res.get("sandbox_build_hash"),
        "sandbox_destruction_hash": watchdog_res.get("sandbox_destruction_hash"),
        "verified_hash": boss_res.get("verified_consensus_hash") or evidence_res.get("sha256_hash"),
    }
    broadcaster_res = await run_b2_broadcaster(comms, broadcaster_payload)

    # Phase 8: Closer (final status + lifecycle)
    closer_payload = {
        "bounty": bounty,
        "accountant": accountant_res,
        "specialist": specialist_res,
        "watchdog": watchdog_res,
        "evidence": evidence_res,
        "boss": boss_res,
        "broadcaster": broadcaster_res,
    }
    closer_res = await run_b2_closer(comms, closer_payload)

    # Neon DB Handoff
    submission = {
        "review_id": boss_res.get("review_id") or f"REV-{bounty_id}-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}",
        "bounty_platform": platform,
        "bounty_id": bounty_id,
        "bounty_title": bounty_title,
        "bounty_url": bounty.get("platform_url"),
        "repo_url": bounty.get("repo_url"),
        "severity": bounty.get("severity", "CRITICAL"),
        "vulnerability_type": bounty.get("vulnerability_type", "smart_contract_audit"),
        "estimated_payout": bounty.get("estimated_payout"),
        "consensus_trials": boss_res.get("consensus_trials", 3),
        "poc_code": poc_code,
        "formatted_submission": broadcaster_res.get("formatted_submission"),
        "pipeline_standards": "BBB Fleet 2 Standard",
        "evidence_chain_hash": evidence_res.get("sha256_hash"),
        "sandbox_build_hash": watchdog_res.get("sandbox_build_hash"),
        "sandbox_destruction_hash": watchdog_res.get("sandbox_destruction_hash"),
        "verified_hash": boss_res.get("verified_consensus_hash"),
        "proof_hash": boss_res.get("verified_consensus_hash"),
        "status": closer_res.get("status", "PENDING_FLEET1_REVIEW"),
        "submission_payload": {
            "bounty": bounty,
            "accountant": accountant_res,
            "specialist": specialist_res,
            "watchdog": watchdog_res,
            "evidence": evidence_res,
            "boss": boss_res,
            "broadcaster": broadcaster_res,
            "closer": closer_res,
        },
    }

    await comms.save_to_handoff(submission)


# ─── Top-Level Runner: 16 Cycles ────────────────────────────────────────

async def run_bounty_cycles():
    """
    Runs up to MAX_CYCLES bounty processing cycles.
    Each cycle:
      - Scanner discovers bounties
      - Each bounty runs through full Fleet 2 pipeline
    """
    comms = BountyComms(agent_id=99, agent_name="Fleet2 Pipeline")
    await comms.startup()

    try:
        for cycle in range(1, MAX_CYCLES + 1):
            print(f"\n[PIPELINE] ===== Cycle {cycle}/{MAX_CYCLES} =====")

            # Phase 1: Scanner
            scanner_payload = {
                "target_platform": TARGET_PLATFORM,
                "cycle_index": cycle,
            }
            scanner_res = await run_b2_scanner(comms, scanner_payload)
            bounties = normalize_scanner_output(scanner_res)

            if not bounties:
                print("[PIPELINE] No bounties discovered this cycle.")
                continue

            for bounty in bounties:
                try:
                    await process_single_bounty(comms, bounty, cycle)
                except Exception as e:
                    print(f"[PIPELINE] Error processing bounty {bounty.get('bounty_id')}: {e}")

    finally:
        await comms.shutdown("Fleet 2 pipeline complete", "", "")


if __name__ == "__main__":
    asyncio.run(run_bounty_cycles())
