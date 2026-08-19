"""
BBB Fleet 2: Bounty Hunters — Agent 5: Gas Requester (Optimization & DoS Specialist)
=====================================================================================
Phase 3 agent. Domain specialist for gas optimization, block limit analysis,
and DoS vulnerability verification on Base mainnet via live Alchemy JSON-RPC queries.
Generates standalone executable PoC scripts for Agent 8 (Watchdog).
"""

import asyncio
import json
import os
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

AGENT_ID = 5
AGENT_NAME = "B2 Gas Requester"


def get_alchemy_rpc_url() -> str:
    """
    Resolves the Alchemy JSON-RPC URL for Base Mainnet from environment variables.
    Checks ALCHEMY_API_KEY and fallbacks (_1, _2, _3, etc.).
    """
    env_keys = [
        "ALCHEMY_API_KEY",
        "ALCHEMY_API_KEY_1",
        "ALCHEMY_API_KEY_2",
        "ALCHEMY_API_KEY_3",
        "ALCHEMY_API_KEY1",
        "ALCHEMY_API_KEY2",
        "ALCHEMY_API_KEY3",
    ]
    for key in env_keys:
        val = os.environ.get(key, "").strip()
        if val:
            if val.startswith("http://") or val.startswith("https://"):
                return val
            return f"https://base-mainnet.g.alchemy.com/v2/{val}"
    return ""


def make_json_rpc_call(rpc_url: str, method: str, params: list) -> dict:
    """
    Executes a JSON-RPC request over HTTPS using stdlib urllib.request.
    """
    if not rpc_url:
        return {"error": {"code": -32000, "message": "No RPC URL configured"}}

    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": method,
        "params": params,
    }
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        rpc_url,
        data=data,
        headers={
            "Content-Type": "application/json",
            "User-Agent": "BBB-Fleet2-GasRequester/1.0",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=15) as response:
            res_body = response.read().decode("utf-8")
            return json.loads(res_body)
    except urllib.error.HTTPError as e:
        try:
            err_body = e.read().decode("utf-8")
            return json.loads(err_body)
        except Exception:
            return {"error": {"code": e.code, "message": f"HTTP Error {e.code}: {e.reason}"}}
    except Exception as e:
        return {"error": {"code": -32603, "message": f"RPC connection error: {str(e)}"}}


def estimate_real_gas(
    target_address: str = "",
    calldata: str = "0x",
    value: str = "0x0",
    from_address: str = "0x0000000000000000000000000000000000000000",
) -> Dict[str, Any]:
    """
    Measures REAL gas for a call to target_address using live Alchemy eth_estimateGas,
    and fetches the live block gas limit via eth_getBlockByNumber('latest').
    """
    rpc_url = get_alchemy_rpc_url()
    if not rpc_url:
        return {
            "success": False,
            "error": "No Alchemy API key configured in environment",
            "gas_estimated": None,
            "block_gas_limit": None,
            "is_dos_viable": False,
        }

    if not target_address or not isinstance(target_address, str) or not target_address.startswith("0x") or len(target_address) != 42:
        return {
            "success": False,
            "error": "Target contract address missing or invalid",
            "gas_estimated": None,
            "block_gas_limit": None,
            "is_dos_viable": False,
        }

    # Fetch live block gas limit
    block_resp = make_json_rpc_call(rpc_url, "eth_getBlockByNumber", ["latest", False])
    if "error" in block_resp or "result" not in block_resp or not block_resp["result"]:
        err_msg = block_resp.get("error", {}).get("message", "Failed to fetch block gas limit")
        return {
            "success": False,
            "error": err_msg,
            "gas_estimated": None,
            "block_gas_limit": None,
            "is_dos_viable": False,
        }

    block_limit_hex = block_resp["result"].get("gasLimit")
    block_gas_limit = int(block_limit_hex, 16) if block_limit_hex else None

    # Estimate gas for target call
    tx_params: Dict[str, str] = {"to": target_address, "data": calldata, "value": value}
    if from_address and isinstance(from_address, str) and from_address.startswith("0x") and len(from_address) == 42:
        tx_params["from"] = from_address

    gas_resp = make_json_rpc_call(rpc_url, "eth_estimateGas", [tx_params])

    if "result" in gas_resp and gas_resp["result"]:
        estimated_gas = int(gas_resp["result"], 16)
        is_dos = (block_gas_limit is not None) and (estimated_gas > block_gas_limit)
        return {
            "success": True,
            "gas_estimated": estimated_gas,
            "block_gas_limit": block_gas_limit,
            "is_dos_viable": is_dos,
            "revert_error": None,
        }
    elif "error" in gas_resp:
        err = gas_resp["error"]
        err_msg = str(err.get("message", ""))
        err_data = str(err.get("data", ""))
        err_full = f"{err_msg} {err_data}".lower()

        oog_keywords = [
            "out of gas",
            "exceeds block gas limit",
            "gas required exceeds allowance",
            "intrinsic gas too low",
            "gas limit exceeded",
            "out-of-gas",
            "unbounded gas",
        ]
        is_unbounded = any(k in err_full for k in oog_keywords)

        return {
            "success": False,
            "error": err_msg,
            "gas_estimated": None,
            "block_gas_limit": block_gas_limit,
            "is_dos_viable": is_unbounded,
            "revert_error": err_msg,
            "is_unbounded_revert": is_unbounded,
        }

    return {
        "success": False,
        "error": "Unexpected JSON-RPC response format",
        "gas_estimated": None,
        "block_gas_limit": block_gas_limit,
        "is_dos_viable": False,
    }


def calculate_simulated_gas_costs(
    target_address: str = "",
    calldata: str = "0x",
    value: str = "0x0",
    from_address: str = "0x0000000000000000000000000000000000000000",
) -> Dict[str, Any]:
    """
    Measures REAL gas costs on Base mainnet via Alchemy JSON-RPC instead of
    invented opcode calculations. Replaces former fake opcode trace simulation.
    """
    if isinstance(target_address, list):
        # Gracefully handle legacy caller passing list of opcodes
        target_address = ""
    return estimate_real_gas(
        target_address=target_address,
        calldata=calldata,
        value=value,
        from_address=from_address,
    )


def generate_gas_poc(
    target_address: str = "",
    calldata: str = "0x",
    value: str = "0x0",
    from_address: str = "0x0000000000000000000000000000000000000000",
) -> str:
    """
    Generates a STANDALONE Python PoC script STRING that Agent 8 (Watchdog) executes.

    The generated script:
    1. Uses Alchemy JSON-RPC to fetch live block gas limit via eth_getBlockByNumber('latest').
    2. Measures real gas for target call via eth_estimateGas.
    3. Exits 0 ONLY if estimated gas exceeds live block gas limit (true DoS/griefing)
       OR reveals a real unbounded-loop out-of-gas estimateGas revert.
    4. Exits 1 otherwise, or if target address is missing/invalid.
    """
    if target_address and not target_address.startswith("0x"):
        target_address = ""

    poc_script = f'''# Standalone Gas DoS & Real Gas Estimation PoC Script
# Executed by Agent 8 (Watchdog)
# Queries live Base mainnet block gas limit and measures real gas usage via Alchemy JSON-RPC.

import os
import sys
import json
import urllib.request
import urllib.error

TARGET_ADDRESS = "{target_address}"
CALLDATA = "{calldata}"
VALUE = "{value}"
FROM_ADDRESS = "{from_address}"

def get_rpc_url():
    env_keys = [
        "ALCHEMY_API_KEY",
        "ALCHEMY_API_KEY_1",
        "ALCHEMY_API_KEY_2",
        "ALCHEMY_API_KEY_3",
        "ALCHEMY_API_KEY1",
        "ALCHEMY_API_KEY2",
        "ALCHEMY_API_KEY3",
    ]
    for key in env_keys:
        val = os.environ.get(key, "").strip()
        if val:
            if val.startswith("http://") or val.startswith("https://"):
                return val
            return f"https://base-mainnet.g.alchemy.com/v2/{{val}}"
    return ""

def rpc_call(url, method, params):
    payload = json.dumps({{
        "jsonrpc": "2.0",
        "id": 1,
        "method": method,
        "params": params
    }}).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=payload,
        headers={{"Content-Type": "application/json", "User-Agent": "BBB-Fleet2-GasPoC/1.0"}},
        method="POST"
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        try:
            return json.loads(e.read().decode("utf-8"))
        except Exception:
            return {{"error": {{"code": e.code, "message": str(e)}}}}
    except Exception as e:
        return {{"error": {{"code": -32603, "message": str(e)}}}}

def run_gas_poc():
    if not TARGET_ADDRESS or not TARGET_ADDRESS.startswith("0x") or len(TARGET_ADDRESS) != 42:
        print(f"[-] Error: Target contract address missing or invalid. Target: '{{TARGET_ADDRESS}}'")
        sys.exit(1)

    rpc_url = get_rpc_url()
    if not rpc_url:
        print("[-] Error: No Alchemy API key configured in environment.")
        sys.exit(1)

    print("[i] Fetching live block gas limit from Base mainnet via Alchemy...")
    block_resp = rpc_call(rpc_url, "eth_getBlockByNumber", ["latest", False])
    if "error" in block_resp or "result" not in block_resp or not block_resp["result"]:
        err_msg = block_resp.get("error", {{}}).get("message", "Unknown error fetching block")
        print(f"[-] Error fetching latest block: {{err_msg}}")
        sys.exit(1)

    block_gas_limit_hex = block_resp["result"].get("gasLimit")
    if not block_gas_limit_hex:
        print("[-] Error: gasLimit missing from block response.")
        sys.exit(1)

    block_gas_limit = int(block_gas_limit_hex, 16)
    block_number = int(block_resp["result"].get("number", "0x0"), 16)
    print(f"[+] Live Block #{{block_number}} Gas Limit: {{block_gas_limit:,}} gas")

    print(f"[i] Measuring real gas via eth_estimateGas for target {{TARGET_ADDRESS}}...")
    tx_params = {{
        "to": TARGET_ADDRESS,
        "data": CALLDATA,
        "value": VALUE,
    }}
    if FROM_ADDRESS and FROM_ADDRESS.startswith("0x") and len(FROM_ADDRESS) == 42:
        tx_params["from"] = FROM_ADDRESS

    gas_resp = rpc_call(rpc_url, "eth_estimateGas", [tx_params])

    if "result" in gas_resp and gas_resp["result"]:
        estimated_gas = int(gas_resp["result"], 16)
        print(f"[+] eth_estimateGas succeeded: {{estimated_gas:,}} gas")

        if estimated_gas > block_gas_limit:
            print(f"[+] VERIFIED GAS DOS / GRIEFING: Estimated gas ({{estimated_gas:,}}) > Block gas limit ({{block_gas_limit:,}})")
            sys.exit(0)
        else:
            print(f"[-] Gas check failed: Estimated gas ({{estimated_gas:,}}) <= Block gas limit ({{block_gas_limit:,}})")
            sys.exit(1)

    elif "error" in gas_resp:
        err = gas_resp["error"]
        err_code = err.get("code", 0)
        err_msg = str(err.get("message", ""))
        err_data = str(err.get("data", ""))
        err_text = f"{{err_msg}} {{err_data}}".lower()

        print(f"[!] eth_estimateGas returned error (code {{err_code}}): {{err_msg}}")

        oog_keywords = [
            "out of gas",
            "exceeds block gas limit",
            "gas required exceeds allowance",
            "intrinsic gas too low",
            "gas limit exceeded",
            "out-of-gas",
            "unbounded gas",
        ]

        if any(keyword in err_text for keyword in oog_keywords):
            print(f"[+] VERIFIED UNBOUNDED LOOP / OUT-OF-GAS REVERT: {{err_msg}}")
            sys.exit(0)
        else:
            print(f"[-] eth_estimateGas reverted without out-of-gas condition: {{err_msg}}")
            sys.exit(1)
    else:
        print("[-] Unexpected JSON-RPC response.")
        sys.exit(1)

if __name__ == "__main__":
    run_gas_poc()
'''
    return poc_script


async def run(comms=None, context: dict = None) -> dict:
    """
    Fleet 2 Standard Agent Entrypoint.
    Executes Phase 3 Gas Optimization analysis and generates PoC using real Alchemy RPC.
    """
    print(f"[{AGENT_NAME}] Phase 3: GAS SPECIALIST analysis started...")

    payload = context or {}
    repo_url = payload.get("repo_url", "")
    bounty_title = payload.get("bounty_title", "Unknown")

    # Gracefully extract target contract address
    target_info = payload.get("target") or {}
    if not isinstance(target_info, dict):
        target_info = {}
    contract_address = (
        target_info.get("contract_address")
        or payload.get("contract_address")
        or ""
    )

    # Gracefully extract source files
    intel = payload.get("intel") or {}
    if not isinstance(intel, dict):
        intel = {}
    repo_data = intel.get("repo_data") or {}
    if not isinstance(repo_data, dict):
        repo_data = {}
    source_files = repo_data.get("source_files", [])

    # Perform real gas estimation via Alchemy RPC
    gas_analysis = calculate_simulated_gas_costs(target_address=contract_address)

    # Generate standalone executable PoC code
    poc_code = generate_gas_poc(target_address=contract_address)

    timestamp_str = datetime.now(timezone.utc).isoformat()

    if contract_address:
        draft = (
            f"Gas Analysis for {bounty_title} ({contract_address}): "
            f"Estimated Gas: {gas_analysis.get('gas_estimated', 'N/A')}, "
            f"Block Limit: {gas_analysis.get('block_gas_limit', 'N/A')}, "
            f"DoS Viable: {gas_analysis.get('is_dos_viable', False)}"
        )
    else:
        draft = (
            f"Gas Analysis for {bounty_title}: "
            f"No target contract_address provided. PoC script prepared with address binding template."
        )

    result = {
        "agent_id": AGENT_ID,
        "agent_name": AGENT_NAME,
        "poc_code": poc_code,
        "draft": draft,
        "timestamp": timestamp_str,
        "contract_address": contract_address,
        "gas_analysis": gas_analysis,
        "is_dos_viable": gas_analysis.get("is_dos_viable", False),
        "source_files": source_files,
    }

    if comms:
        await comms.save_pipeline_log(
            "phase_3_gas",
            f"Gas specialist analysis complete for '{bounty_title}'. DoS Viable: {gas_analysis.get('is_dos_viable', False)}"
        )

    print(f"[{AGENT_NAME}] Gas analysis complete.")
    return result


async def main():
    from core.bounty_comms import BountyComms

    comms = BountyComms(AGENT_ID, AGENT_NAME)
    await comms.startup()

    context = {
        "bounty_title": "Base Mainnet Gas Vulnerability Check",
        "repo_url": "https://github.com/example/gas-vulnerable-repo",
        "target": {
            "contract_address": "0x0000000000000000000000000000000000000000",
        },
        "intel": {
            "repo_data": {
                "source_files": ["contracts/Target.sol"]
            }
        },
    }
    result = await run(comms, context)
    print(f"  -> Gas cost analysis draft: {result.get('draft')}")
    print(f"  -> PoC Code generated ({len(result.get('poc_code', ''))} bytes)")
    await comms.shutdown()


if __name__ == "__main__":
    asyncio.run(main())
