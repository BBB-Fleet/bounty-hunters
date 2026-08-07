import os
import json
import asyncio
import aiohttp
import asyncpg
from datetime import datetime, timezone
from core.bounty_shared_config import UPSTASH_REDIS_URL, UPSTASH_REDIS_TOKEN, NEON_CONNECTION_STRING

MAX_RETRIES = 3
RETRY_DELAY = 2

class AgentComms:
    def __init__(self, agent_id: int, agent_name: str):
        self.agent_id = agent_id
        self.agent_name = agent_name
        self.redis_url = UPSTASH_REDIS_URL
        self.redis_token = UPSTASH_REDIS_TOKEN
        self.neon_conn = NEON_CONNECTION_STRING
        self._pg_conn = None

    async def _get_pg(self):
        if self._pg_conn is None or self._pg_conn.is_closed():
            self._pg_conn = await asyncpg.connect(self.neon_conn)
        return self._pg_conn

    async def _pg_execute(self, query, *args, retries=MAX_RETRIES):
        for attempt in range(retries):
            try:
                conn = await self._get_pg()
                return await conn.execute(query, *args)
            except Exception as e:
                if attempt == retries - 1:
                    raise e
                await asyncio.sleep(RETRY_DELAY)
                self._pg_conn = None

    async def _pg_fetchrow(self, query, *args, retries=MAX_RETRIES):
        for attempt in range(retries):
            try:
                conn = await self._get_pg()
                return await conn.fetchrow(query, *args)
            except Exception as e:
                if attempt == retries - 1:
                    raise e
                await asyncio.sleep(RETRY_DELAY)
                self._pg_conn = None

    async def _pg_fetch(self, query, *args, retries=MAX_RETRIES):
        for attempt in range(retries):
            try:
                conn = await self._get_pg()
                return await conn.fetch(query, *args)
            except Exception as e:
                if attempt == retries - 1:
                    raise e
                await asyncio.sleep(RETRY_DELAY)
                self._pg_conn = None

    async def init_db(self):
        await self._pg_execute("""
            CREATE TABLE IF NOT EXISTS bounty_agent_state (
                agent_id INT PRIMARY KEY,
                state_data TEXT,
                updated_at TIMESTAMP DEFAULT NOW()
            )
        """)
        await self._pg_execute("""
            CREATE TABLE IF NOT EXISTS bounty_daily_summaries (
                id SERIAL PRIMARY KEY,
                summary TEXT,
                created_at TIMESTAMP DEFAULT NOW()
            )
        """)
        await self._pg_execute("""
            CREATE TABLE IF NOT EXISTS bounty_pipeline_log (
                id SERIAL PRIMARY KEY,
                log_data TEXT,
                created_at TIMESTAMP DEFAULT NOW()
            )
        """)
        await self._pg_execute("""
            CREATE TABLE IF NOT EXISTS bbb_fleet_handoff (
                id SERIAL PRIMARY KEY,
                source_fleet TEXT DEFAULT 'fleet2',
                submission_id TEXT UNIQUE,
                bounty_platform TEXT,
                bounty_id TEXT,
                bounty_title TEXT,
                bounty_url TEXT,
                submission_payload TEXT,
                estimated_payout DECIMAL(12,2),
                requires_onchain BOOLEAN DEFAULT false,
                gas_estimate_eth DECIMAL(18,8),
                consensus_trials INT DEFAULT 1,
                status TEXT DEFAULT 'PENDING_FLEET1_REVIEW',
                splits_vault TEXT DEFAULT '0xc87c3e8CB21e5A630Baf8D38b2060aCBb047afCb',
                fleet1_review_notes TEXT,
                created_at TIMESTAMP DEFAULT NOW(),
                reviewed_at TIMESTAMP
            )
        """)
        await self._pg_execute("""
            CREATE TABLE IF NOT EXISTS bounty_lifecycle_log (
                id SERIAL PRIMARY KEY,
                bounty_id TEXT,
                bounty_title TEXT,
                platform TEXT,
                payout_usd DECIMAL(12,2),
                bounty_type TEXT,
                assigned_specialists TEXT,
                consensus_trials INT,
                strategies_used TEXT,
                status TEXT,
                deciding_agent_id INT,
                submission_payload TEXT,
                created_at TIMESTAMP DEFAULT NOW(),
                updated_at TIMESTAMP DEFAULT NOW()
            )
        """)
        await self._pg_execute("""
            CREATE TABLE IF NOT EXISTS bounty_api_metrics (
                id SERIAL PRIMARY KEY,
                api_key TEXT,
                endpoint TEXT,
                items_returned INT,
                response_time_ms INT,
                created_at TIMESTAMP DEFAULT NOW()
            )
        """)

    async def publish(self, channel, message):
        pass

    async def subscribe(self, channel):
        pass

    async def set_latest(self, channel, message):
        pass

    async def heartbeat(self):
        pass

    async def save_state(self, key, value):
        state_json = json.dumps({key: value})
        await self._pg_execute("""
            INSERT INTO bounty_agent_state (agent_id, state_data, updated_at)
            VALUES ($1, $2, NOW())
            ON CONFLICT (agent_id) DO UPDATE SET state_data = $2, updated_at = NOW()
        """, self.agent_id, state_json)

    async def recall_state(self):
        row = await self._pg_fetchrow("SELECT state_data FROM bounty_agent_state WHERE agent_id=$1", self.agent_id)
        if row:
            return json.loads(row['state_data'])
        return {}

    async def save_summary(self, summary):
        await self._pg_execute("INSERT INTO bounty_daily_summaries (summary) VALUES ($1)", summary)

    async def save_pipeline_log(self, phase: str, message: str):
        log_entry = json.dumps({"agent_id": self.agent_id, "agent_name": self.agent_name, "phase": phase, "message": message, "timestamp": datetime.now(timezone.utc).isoformat()})
        await self._pg_execute("INSERT INTO bounty_pipeline_log (log_data) VALUES ($1)", log_entry)

    async def startup(self):
        await self.init_db()

    async def shutdown(self, *args, **kwargs):
        if self._pg_conn and not self._pg_conn.is_closed():
            await self._pg_conn.close()

    async def save_to_handoff(self, submission: dict):
        await self._pg_execute("""
            INSERT INTO bbb_fleet_handoff (
                submission_id, bounty_platform, bounty_id, bounty_title, bounty_url, 
                submission_payload, estimated_payout, requires_onchain, gas_estimate_eth,
                consensus_trials
            ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)
        """, submission.get('submission_id'), submission.get('bounty_platform'), submission.get('bounty_id'),
             submission.get('bounty_title'), submission.get('bounty_url'), json.dumps(submission.get('submission_payload')),
             submission.get('estimated_payout'), submission.get('requires_onchain', False), submission.get('gas_estimate_eth', 0.0),
             submission.get('consensus_trials', 1))

    async def read_fleet1_state(self, agent_id: int):
        row = await self._pg_fetchrow("SELECT state_data FROM bbb_agent_state WHERE agent_id=$1", agent_id)
        if row:
            return json.loads(row['state_data'])
        return {}

    async def save_bounty_lifecycle(self, bounty_id: str, bounty_title: str, platform: str, payout_usd: float,
                                    bounty_type: str, assigned_specialists: str, consensus_trials: int,
                                    strategies_used: str, status: str, deciding_agent_id: int, submission_payload: str):
        # We use an UPSERT logic based on bounty_id to avoid creating duplicates for the same hunt
        # Wait, there's no UNIQUE constraint on bounty_id in the schema... let's just use a simple check or INSERT
        # Actually, it's safer to just INSERT a new record when the lifecycle status changes.
        await self._pg_execute("""
            INSERT INTO bounty_lifecycle_log (
                bounty_id, bounty_title, platform, payout_usd, bounty_type, 
                assigned_specialists, consensus_trials, strategies_used, 
                status, deciding_agent_id, submission_payload
            ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11)
        """, bounty_id, bounty_title, platform, payout_usd, bounty_type, 
             assigned_specialists, consensus_trials, strategies_used, 
             status, deciding_agent_id, submission_payload)

    async def save_api_metric(self, api_key: str, endpoint: str, items_returned: int, response_time_ms: int):
        await self._pg_execute("""
            INSERT INTO bounty_api_metrics (api_key, endpoint, items_returned, response_time_ms)
            VALUES ($1, $2, $3, $4)
        """, api_key, endpoint, items_returned, response_time_ms)

BountyComms = AgentComms
