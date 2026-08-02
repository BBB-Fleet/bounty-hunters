"""
BBB Fleet 2: Bounty Hunters — Agent 10: Boss (Bounty Pipeline Orchestrator)
===========================================================================
MAIN ORCHESTRATOR FOR FLEET 2.
Executes the full 7-Phase Bounty Pipeline:
  Phase 1: The Hunt (b2_11_closer)
  Phase 2: Internal Approval (b2_10_boss + b2_2_accountant)
  Phase 3: Intel Gathering (b2_1_scanner)
  Phase 4: The War Room (Specialist + b2_8_watchdog)
  Phase 5: Consensus Loop (100% agreement required, max 3 trials)
  Phase 6: Packaging (b2_9_broadcaster + b2_11_closer review)
  Phase 7: Invoice Submission (b2_2_accountant -> bbb_fleet_handoff table)
"""

import asyncio
import json
import sys
from datetime import datetime

from agents import (
    b2_1_scanner,
    b2_2_accountant,
    b2_3_bridge,
    b2_4_lender,
    b2_5_gas_requester,
    b2_6_solana_ghost,
    b2_7_minter,
    b2_8_watchdog,
    b2_9_broadcaster,
    b2_11_closer,
)
from core.bounty_comms import BountyComms
from core.bounty_shared_config import MAX_CONSENSUS_TRIALS, SPECIALIST_MAPPING

AGENT_ID = 10
AGENT_NAME = "B2 Boss"


def get_specialist(bounty_type: str):
    """Map bounty type to specialist module."""
    mapping = {
        "smart_contract_audit": b2_7_minter,
        "defi_vulnerability": b2_4_lender,
        "cross_chain_bridge": b2_3_bridge,
        "solana_rust": b2_6_solana_ghost,
        "sdk_tooling": b2_5_gas_requester,
        "documentation": b2_5_gas_requester,
    }
    return mapping.get(bounty_type, b2_5_gas_requester)


async def run_pipeline(comms: BountyComms) -> dict:
    """Execute the 7-Phase Bounty Pipeline."""
    print("\n" + "=" * 60)
    print("BBB FLEET 2: BOUNTY HUNTERS -- PIPELINE STARTING")
    print("=" * 60 + "\n")

    pipeline_summary = {
        "pipeline_run_id": f"RUN-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
        "timestamp": datetime.utcnow().isoformat(),
        "phases": {},
        "status": "in_progress"
    }

    # =========================================================================
    # PHASE 1: THE HUNT
    # =========================================================================
    print("\n[PHASE 1] THE HUNT -- Scouting bounty platforms...")
    hunt_result = await b2_11_closer.run(comms)
    pipeline_summary["phases"]["1_hunt"] = {
        "bounties_found": hunt_result.get("bounties_found", 0)
    }

    discovered = hunt_result.get("bounties", [])
    if not discovered:
        print("[PHASE 1] ⚠️ No open bounties discovered. Pipeline exiting cleanly.")
        pipeline_summary["status"] = "completed_no_bounties"
        return pipeline_summary

    # Select candidate bounty
    target_bounty = discovered[0]
    print(f"[PHASE 1] Target Bounty Selected: [{target_bounty.get('platform')}] {target_bounty.get('title')}")

    # =========================================================================
    # PHASE 2: INTERNAL APPROVAL
    # =========================================================================
    print("\n[PHASE 2] INTERNAL APPROVAL -- Evaluating ROI & fleet match...")
    eval_result = await b2_2_accountant.run(comms, {"action": "evaluate", "bounty": target_bounty})
    pipeline_summary["phases"]["2_approval"] = eval_result

    if not eval_result.get("approved", False):
        print(f"[PHASE 2] Bounty Rejected: {eval_result.get('reason')}")
        pipeline_summary["status"] = "rejected_in_phase_2"
        return pipeline_summary
    print(f"[PHASE 2] Approved! ROI Score: {eval_result.get('roi_score')}")

    # =========================================================================
    # PHASE 3: INTEL GATHERING
    # =========================================================================
    print("\n[PHASE 3] INTEL GATHERING -- Scraping code & master data...")
    intel_result = await b2_1_scanner.run(comms, target_bounty)
    pipeline_summary["phases"]["3_intel"] = {
        "files_scraped": intel_result.get("files_scraped", 0)
    }

    # =========================================================================
    # PHASE 4 & 5: WAR ROOM & CONSENSUS LOOP
    # =========================================================================
    print("\n[PHASE 4 & 5] WAR ROOM & CONSENSUS LOOP -- Solving & Auditing...")
    specialist_mod = get_specialist(target_bounty.get("bounty_type", "sdk_tooling"))

    trial = 1
    consensus_reached = False
    final_draft = None
    final_audit = None

    while trial <= MAX_CONSENSUS_TRIALS and not consensus_reached:
        print(f"\n--- CONSENSUS TRIAL {trial}/{MAX_CONSENSUS_TRIALS} ---")

        # Step A: Specialist formulates solution
        draft_res = await specialist_mod.run(comms, intel_result.get("intel", {}))

        # Step B: Watchdog audits draft
        audit_res = await b2_8_watchdog.run(comms, draft_res)

        # Step C: Collect votes
        votes = [
            {"agent": "Scanner", "vote": "AGREE", "reason": "Data matched"},
            {"agent": "Accountant", "vote": eval_result.get("vote", "AGREE"), "reason": eval_result.get("reason")},
            {"agent": draft_res.get("agent"), "vote": draft_res.get("vote", "AGREE"), "reason": draft_res.get("reason")},
            {"agent": "Watchdog", "vote": audit_res.get("vote", "AGREE"), "reason": audit_res.get("reason")}
        ]

        # Tally consensus
        disagreements = [v for v in votes if v["vote"] != "AGREE"]

        if not disagreements:
            print(f"CONSENSUS ACHIEVED ON TRIAL {trial}! All participating agents VOTE AGREE!")
            consensus_reached = True
            final_draft = draft_res
            final_audit = audit_res
        else:
            print(f"CONSENSUS FAILED ON TRIAL {trial}. Disagreements:")
            for d in disagreements:
                print(f"   - [{d['agent']}]: {d['reason']}")
            trial += 1
            await asyncio.sleep(1)

    pipeline_summary["phases"]["4_5_consensus"] = {
        "trials_took": trial if consensus_reached else MAX_CONSENSUS_TRIALS,
        "consensus_achieved": consensus_reached
    }

    if not consensus_reached:
        print("\n[PHASE 5] Pipeline Failed: Consensus could not be reached within 3 trials.")
        pipeline_summary["status"] = "failed_consensus"
        return pipeline_summary

    # =========================================================================
    # PHASE 6: PACKAGING
    # =========================================================================
    print("\n[PHASE 6] PACKAGING -- Formatting submission payload...")
    package_context = {
        "platform": target_bounty.get("platform", "algora"),
        "bounty_title": target_bounty.get("title", ""),
        "bounty_id": target_bounty.get("bounty_id", ""),
        "draft": final_draft.get("draft", ""),
        "audit": final_audit.get("audit_report", ""),
        "estimated_payout": eval_result.get("estimated_payout", 100.0),
        "requires_onchain": final_draft.get("requires_onchain", False),
        "gas_estimate_eth": final_draft.get("gas_estimate_eth", 0.0),
        "consensus_trials": trial
    }

    package_res = await b2_9_broadcaster.run(comms, package_context)
    pipeline_summary["phases"]["6_packaging"] = {
        "formatted_size": len(package_res.get("formatted_submission", ""))
    }

    # =========================================================================
    # PHASE 7: INVOICE SUBMISSION TO FLEET 1
    # =========================================================================
    print("\n[PHASE 7] INVOICE -- Handing off submission to Fleet 1...")
    submit_res = await b2_2_accountant.run(comms, {"action": "submit", "bounty": package_res})
    pipeline_summary["phases"]["7_invoice"] = submit_res
    pipeline_summary["status"] = "completed_submitted_to_fleet1"

    print("\n" + "=" * 60)
    print(f"SUCCESS! Submission {submit_res.get('submission_id')} sent to Fleet 1 Review Bridge!")
    print("=" * 60 + "\n")

    return pipeline_summary


async def main():
    comms = BountyComms(AGENT_ID, AGENT_NAME)
    await comms.startup()

    summary = await run_pipeline(comms)

    await comms.save_state("pipeline_status", json.dumps(summary))
    await comms.shutdown()


if __name__ == "__main__":
    asyncio.run(main())
