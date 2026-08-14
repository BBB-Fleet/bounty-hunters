"""
BBB Fleet 2 — GitHub Bounty Intel & Target Scope Extractor
=========================================================
Extracts real repository scope, smart contracts, security policies, 
and documentation for bug bounty targets matching TARGET_DISCOVERY_RULES.
Read-only reconnaissance: No live submissions, no forks, no issues created.
"""

import base64
import os
from typing import Dict, List, Optional, Union
import aiohttp
from dotenv import load_dotenv

load_dotenv()


def _get_headers() -> dict:
    """Dynamically generates GitHub API headers using GITHUB_TOKEN if present."""
    token = os.environ.get("GITHUB_TOKEN")
    headers = {
        "Accept": "application/vnd.github.v3+json",
        "User-Agent": "BBB-Fleet2-BountyScanner/4.0",
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return headers


async def search_bounty_issues(
    labels: Optional[List[str]] = None,
    language: Optional[str] = None,
    limit: int = 20,
    timeout_seconds: int = 15,
) -> list:
    """Searches for public bounty issues, scope announcements, or security programs."""
    if labels is None:
        labels = ["bounty"]

    url = "https://api.github.com/search/issues"
    query = "state:open"
    if labels:
        query += " " + " ".join([f'label:"{l}"' for l in labels])
    if language:
        query += f" language:{language}"

    params = {"q": query, "per_page": limit}
    headers = _get_headers()

    async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=timeout_seconds)) as session:
        try:
            async with session.get(url, params=params, headers=headers) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    return data.get("items", [])
        except Exception:
            pass
    return []


async def get_repo_contents(
    owner: str,
    repo: str,
    path: str = "",
    timeout_seconds: int = 15,
) -> Union[dict, list, None]:
    """Fetches directory listings or raw file metadata from a target repository."""
    url = f"https://api.github.com/repos/{owner}/{repo}/contents/{path}"
    headers = _get_headers()

    async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=timeout_seconds)) as session:
        try:
            async with session.get(url, headers=headers) as resp:
                if resp.status == 200:
                    return await resp.json()
        except Exception:
            pass
    return None


async def extract_security_policy(
    owner: str,
    repo: str,
    timeout_seconds: int = 15,
) -> Optional[str]:
    """Retrieves SECURITY.md or bug bounty policy from the target repository."""
    candidate_paths = ["SECURITY.md", ".github/SECURITY.md", "docs/SECURITY.md", "README.md"]
    for path in candidate_paths:
        data = await get_repo_contents(owner, repo, path=path, timeout_seconds=timeout_seconds)
        if isinstance(data, dict) and data.get("content"):
            try:
                decoded = base64.b64decode(data["content"]).decode("utf-8", errors="ignore")
                return decoded
            except Exception:
                pass
    return None


async def discover_target_contracts_and_files(
    owner: str,
    repo: str,
    timeout_seconds: int = 15,
) -> Dict[str, List[str]]:
    """
    Extracts contracts and core target source files conforming to TARGET_DISCOVERY_RULES:
    Identifies Solidity, Rust, Vyper, and TypeScript contracts/protocols.
    """
    discovered = {
        "contracts": [],
        "documentation": [],
        "tooling": []
    }

    # Inspect common contract and source roots
    search_dirs = ["", "contracts", "src", "programs", "core", "packages"]
    for directory in search_dirs:
        items = await get_repo_contents(owner, repo, path=directory, timeout_seconds=timeout_seconds)
        if isinstance(items, list):
            for item in items:
                path = item.get("path", "")
                if path.endswith((".sol", ".rs", ".vy")):
                    discovered["contracts"].append(path)
                elif path.endswith((".md", ".rst", ".pdf")):
                    discovered["documentation"].append(path)
                elif path.endswith((".ts", ".js", ".py")):
                    discovered["tooling"].append(path)

    return discovered
