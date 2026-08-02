import os
import json
import time
import asyncio
import aiohttp
from core.bounty_shared_config import GROQ_API_KEY, OLLAMA_BASE_URL, OLLAMA_MODEL

last_request_time = 0

async def query_llm(prompt: str, system_prompt: str = '', temperature: float = 0.7, max_tokens: int = 1024) -> str:
    global last_request_time
    
    use_groq = bool(GROQ_API_KEY)
    
    if use_groq:
        current_time = time.time()
        time_since_last = current_time - last_request_time
        if time_since_last < 2.0:
            await asyncio.sleep(2.0 - time_since_last)
        last_request_time = time.time()
        
        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": "llama-3.1-8b-instant",
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ],
            "temperature": temperature,
            "max_tokens": max_tokens
        }
    else:
        url = f"{OLLAMA_BASE_URL}/api/generate"
        headers = {"Content-Type": "application/json"}
        payload = {
            "model": OLLAMA_MODEL,
            "system": system_prompt,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens
            }
        }
    
    retries = 3
    for attempt in range(retries):
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, headers=headers, json=payload, timeout=60) as resp:
                    if resp.status == 429:
                        await asyncio.sleep(2 ** attempt)
                        continue
                    resp.raise_for_status()
                    data = await resp.json()
                    
                    if use_groq:
                        return data['choices'][0]['message']['content']
                    else:
                        return data['response']
        except Exception as e:
            if attempt == retries - 1:
                raise e
            await asyncio.sleep(2 ** attempt)
