import os
import aiohttp

GITHUB_TOKEN = os.environ.get('GITHUB_TOKEN')

async def search_bounty_issues(labels=['bounty'], language=None, limit=20) -> list:
    url = "https://api.github.com/search/issues"
    query = "state:open"
    if labels:
        query += " " + " ".join([f'label:"{l}"' for l in labels])
    if language:
        query += f" language:{language}"
    
    params = {'q': query, 'per_page': limit}
    headers = {'Authorization': f'token {GITHUB_TOKEN}', 'Accept': 'application/vnd.github.v3+json'} if GITHUB_TOKEN else {'Accept': 'application/vnd.github.v3+json'}
    
    async with aiohttp.ClientSession() as session:
        async with session.get(url, params=params, headers=headers) as resp:
            resp.raise_for_status()
            data = await resp.json()
            return data.get('items', [])

async def get_repo_contents(owner, repo, path='') -> dict:
    url = f"https://api.github.com/repos/{owner}/{repo}/contents/{path}"
    headers = {'Authorization': f'token {GITHUB_TOKEN}', 'Accept': 'application/vnd.github.v3+json'} if GITHUB_TOKEN else {'Accept': 'application/vnd.github.v3+json'}
    
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as resp:
            resp.raise_for_status()
            return await resp.json()

async def create_issue(owner, repo, title, body, labels=[]) -> str:
    url = f"https://api.github.com/repos/{owner}/{repo}/issues"
    headers = {'Authorization': f'token {GITHUB_TOKEN}', 'Accept': 'application/vnd.github.v3+json'}
    payload = {'title': title, 'body': body, 'labels': labels}
    
    async with aiohttp.ClientSession() as session:
        async with session.post(url, headers=headers, json=payload) as resp:
            resp.raise_for_status()
            data = await resp.json()
            return data.get('html_url')

async def create_pull_request(owner, repo, title, body, head, base='main') -> str:
    url = f"https://api.github.com/repos/{owner}/{repo}/pulls"
    headers = {'Authorization': f'token {GITHUB_TOKEN}', 'Accept': 'application/vnd.github.v3+json'}
    payload = {'title': title, 'body': body, 'head': head, 'base': base}
    
    async with aiohttp.ClientSession() as session:
        async with session.post(url, headers=headers, json=payload) as resp:
            resp.raise_for_status()
            data = await resp.json()
            return data.get('html_url')

async def fork_repo(owner, repo) -> dict:
    url = f"https://api.github.com/repos/{owner}/{repo}/forks"
    headers = {'Authorization': f'token {GITHUB_TOKEN}', 'Accept': 'application/vnd.github.v3+json'}
    
    async with aiohttp.ClientSession() as session:
        async with session.post(url, headers=headers) as resp:
            resp.raise_for_status()
            return await resp.json()
