"""
BBB Fleet 2: Bounty Hunters — Agent 1: Scanner (Bounty Intel Scraper)
=====================================================================
Phase 3 agent. Receives an approved bounty and scrapes all raw data
needed for the specialists to work on it.
"""

import asyncio
import json
from datetime import datetime

import aiohttp

AGENT_ID = 1
AGENT_NAME = "B2 Scanner"


async def _fetch_text(url: str, max_chars: int = 2000) -> str:
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=15)) as resp:
                if resp.status == 200:
                    text = await resp.text()
                    return text[:max_chars]
    except Exception as e:
        return f"[Fetch error: {e}]"
    return ""


async def scrape_github_repo(repo_url: str) -> dict:
    """Fetch README and key source files from a GitHub repo."""
    intel = {"readme": "", "source_files": [], "repo_url": repo_url}

    # Extract owner/repo from URL
    parts = repo_url.replace("https://github.com/", "").split("/")
    if len(parts) < 2:
        return intel
    owner, repo = parts[0], parts[1].split("/")[0].split("?")[0].split("#")[0]

    # Fetch README
    readme_url = f"https://raw.githubusercontent.com/{owner}/{repo}/main/README.md"
    intel["readme"] = await _fetch_text(readme_url, 3000)
    if not intel["readme"] or "404" in intel["readme"][:50]:
        readme_url = f"https://raw.githubusercontent.com/{owner}/{repo}/master/README.md"
        intel["readme"] = await _fetch_text(readme_url, 3000)

    # Fetch repo tree for key files
    api_url = f"https://api.github.com/repos/{owner}/{repo}/git/trees/main?recursive=1"
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(api_url, timeout=aiohttp.ClientTimeout(total=15)) as resp:
                if resp.status == 200:
                    tree_data = await resp.json()
                    files = [f["path"] for f in tree_data.get("tree", [])
                             if f["type"] == "blob" and any(
                                 f["path"].endswith(ext)
                                 for ext in [".sol", ".rs", ".py", ".ts", ".js", ".go"]
                             )]
                    # Fetch up to 5 key source files
                    for fpath in files[:5]:
                        raw_url = f"https://raw.githubusercontent.com/{owner}/{repo}/main/{fpath}"
                        content = await _fetch_text(raw_url, 2000)
                        if content:
                            intel["source_files"].append({"path": fpath, "content": content})
    except Exception:
        pass

    return intel


async def run(comms, context: dict = None) -> dict:
    """Main agent function called by the Boss pipeline."""
    bounty = context or {}
    print(f"[{AGENT_NAME}] Phase 3: INTEL GATHERING for '{bounty.get('title', 'Unknown')}'")

    intel = {
        "bounty_id": bounty.get("bounty_id", "unknown"),
        "bounty_title": bounty.get("title", "Unknown"),
        "bounty_type": bounty.get("bounty_type", "sdk_tooling"),
        "bounty_description": bounty.get("description", ""),
        "platform": bounty.get("platform", "unknown"),
        "repo_data": {},
        "analysis": "",
        "timestamp": datetime.utcnow().isoformat()
    }

    # Scrape repo if URL available
    repo_url = bounty.get("repo_url", "")
    if repo_url and "github.com" in repo_url:
        print(f"[{AGENT_NAME}] Scraping GitHub repo: {repo_url}")
        intel["repo_data"] = await scrape_github_repo(repo_url)

    # Use LLM to summarize collected intel
    from core.llm_client import query_llm
    summary_prompt = (
        f"You are a security researcher analyzing a bounty.\n"
        f"Bounty: {bounty.get('title', 'Unknown')}\n"
        f"Description: {bounty.get('description', '')[:500]}\n"
        f"Type: {bounty.get('bounty_type', 'unknown')}\n"
        f"README excerpt: {intel['repo_data'].get('readme', '')[:1000]}\n\n"
        f"Summarize the key areas to investigate. List the 3 most promising attack vectors "
        f"or contribution areas. Be specific and technical. 200 words max."
    )
    intel["analysis"] = await query_llm(summary_prompt)

    result = {
        "agent": AGENT_NAME,
        "phase": "intel_gathering",
        "intel": intel,
        "files_scraped": len(intel["repo_data"].get("source_files", [])),
        "timestamp": datetime.utcnow().isoformat()
    }

    if comms:
        await comms.save_state("bounty_intel", json.dumps(result))
        await comms.save_pipeline_log("phase_3_intel", f"Gathered intel: {result['files_scraped']} files scraped")

    print(f"[{AGENT_NAME}] Intel complete: {result['files_scraped']} source files analyzed")
    return result


async def main():
    from core.bounty_comms import BountyComms
    comms = BountyComms(AGENT_ID, AGENT_NAME)
    await comms.startup()
    result = await run(comms, {"title": "Test bounty", "repo_url": "", "bounty_type": "sdk_tooling"})
    await comms.shutdown(str(result)[:500], "", "")

if __name__ == "__main__":
    asyncio.run(main())
