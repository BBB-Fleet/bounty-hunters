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
            CREATE TABLE IF NOT EXISTS bbb_commercial_services_log (
                id SERIAL PRIMARY KEY,
                category TEXT NOT NULL,
                item_key TEXT,
                item_name TEXT,
                masked_value TEXT,
                details JSONB,
                created_at TIMESTAMP DEFAULT NOW()
            );
        """)
        await self._pg_execute("""
            CREATE TABLE IF NOT EXISTS bbb_bounty_master_ledger (
                id SERIAL PRIMARY KEY,
                review_id TEXT UNIQUE NOT NULL,
                source_fleet TEXT DEFAULT 'fleet2',
                record_type TEXT DEFAULT 'REAL_RUN',
                bounty_platform TEXT,
                bounty_id TEXT,
                bounty_title TEXT,
                platform_url TEXT,
                repo_url TEXT,
                severity TEXT DEFAULT 'CRITICAL',
                vulnerability_type TEXT,
                estimated_payout DECIMAL(12,2) DEFAULT 0.00,
                consensus_trials INT DEFAULT 3,
                poc_code TEXT,
                formatted_submission TEXT,
                pipeline_standards TEXT,
                evidence_chain_hash TEXT,
                sandbox_build_hash TEXT,
                sandbox_destruction_hash TEXT,
                verified_hash TEXT,
                proof_hash TEXT,
                status TEXT DEFAULT 'PENDING_FLEET1_REVIEW',
                fleet1_review_notes TEXT,
                payload JSONB,
                created_at TIMESTAMP DEFAULT NOW(),
                reviewed_at TIMESTAMP
            );
        """)

    async def save_state(self, key, value):
        state_json = json.dumps({key: value})
        await self._pg_execute("""
            INSERT INTO bbb_commercial_services_log (category, item_key, item_name, details, created_at)
            VALUES ($1, $2, $3, $4, NOW())
        """, "AGENT_STATE", f"agent_{self.agent_id}", self.agent_name, state_json)

    async def save_summary(self, summary):
        await self._pg_execute("""
            INSERT INTO bbb_daily_summaries (summary, created_at)
            VALUES ($1, NOW())
        """, summary)

    async def save_pipeline_log(self, phase: str, message: str):
        rev_id = f"LOG-{self.agent_id}-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S%f')}"
        log_meta = {"agent_id": self.agent_id, "agent_name": self.agent_name, "phase": phase, "message": message}
        await self._pg_execute("""
            INSERT INTO bbb_bounty_master_ledger (
                review_id, source_fleet, record_type, status, fleet1_review_notes, payload, created_at
            ) VALUES ($1, 'fleet2', 'PIPELINE_LOG', 'LOGGED', $2, $3, NOW())
            ON CONFLICT (review_id) DO NOTHING
        """, rev_id, f"[{phase}] {message}", json.dumps(log_meta))

    async def startup(self):
        await self.init_db()

    async def shutdown(self, *args, **kwargs):
        if self._pg_conn and not self._pg_conn.is_closed():
            await self._pg_conn.close()

    async def save_to_handoff(self, submission: dict):
        rev_id = submission.get('review_id') or submission.get('submission_id') or f"REV-B2-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}"
        if rev_id.startswith("SUB-"):
            rev_id = rev_id.replace("SUB-", "REV-")
            
        payload_meta = json.dumps(submission.get('submission_payload', submission))
        payout_val = float(submission.get('estimated_payout') or 0.0)
        consensus_val = int(submission.get('consensus_trials') or 3)
        
        await self._pg_execute("""
            INSERT INTO bbb_bounty_master_ledger (
                review_id, source_fleet, record_type, bounty_platform, bounty_id, bounty_title,
                platform_url, repo_url, severity, vulnerability_type, estimated_payout,
                consensus_trials, poc_code, formatted_submission, pipeline_standards,
                evidence_chain_hash, sandbox_build_hash, sandbox_destruction_hash,
                status, payload, created_at
            ) VALUES ($1, 'fleet2', 'REAL_RUN', $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15, $16, $17, $18, NOW())
            ON CONFLICT (review_id) DO UPDATE SET
                payload = EXCLUDED.payload,
                status = 'PENDING_FLEET1_REVIEW',
                created_at = NOW()
        """, rev_id, submission.get('bounty_platform'), submission.get('bounty_id'),
             submission.get('bounty_title'), submission.get('bounty_url') or submission.get('platform_url'),
             submission.get('repo_url'), submission.get('severity', 'CRITICAL'),
             submission.get('vulnerability_type', 'smart_contract_audit'), payout_val,
             consensus_val, submission.get('poc_code'), submission.get('formatted_submission'),
             submission.get('pipeline_standards'), submission.get('evidence_chain_hash'),
             submission.get('sandbox_build_hash'), submission.get('sandbox_destruction_hash'),
             submission.get('status', 'PENDING_FLEET1_REVIEW'), payload_meta)

    async def save_bounty_lifecycle(self, bounty_id: str, bounty_title: str, platform: str, payout_usd: float,
                                    bounty_type: str, assigned_specialists: str, consensus_trials: int,
                                    strategies_used: str, status: str, deciding_agent_id: int, submission_payload: str,
                                    platform_url: str = None, repo_url: str = None, severity: str = None,
                                    evidence_chain_hash: str = None, pipeline_standards: str = None, poc_code: str = None,
                                    review_id: str = None):
        rev_id = review_id or f"REV-LIFECYCLE-{bounty_id}-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}"
        if rev_id.startswith("SUB-"):
            rev_id = rev_id.replace("SUB-", "REV-")

        await self._pg_execute("""
            INSERT INTO bbb_bounty_master_ledger (
                review_id, source_fleet, record_type, bounty_platform, bounty_id, bounty_title,
                platform_url, repo_url, severity, vulnerability_type, estimated_payout,
                consensus_trials, evidence_chain_hash, pipeline_standards, poc_code,
                status, fleet1_review_notes, payload, created_at
            ) VALUES ($1, 'fleet2', 'LIFECYCLE_LOG', $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15, $16, NOW())
            ON CONFLICT (review_id) DO UPDATE SET status = EXCLUDED.status, reviewed_at = NOW()
        """, rev_id, platform, bounty_id, bounty_title, platform_url, repo_url, severity or 'CRITICAL',
             bounty_type, payout_usd, consensus_trials, evidence_chain_hash, pipeline_standards,
             poc_code, status, f"Assigned Specialists: {assigned_specialists}. Strategy: {strategies_used}",
             submission_payload)

    async def save_api_metric(self, api_key: str, endpoint: str, items_returned: int, response_time_ms: int):
        await self._pg_execute("""
            INSERT INTO bounty_api_metrics (api_key, endpoint, items_returned, response_time_ms)
            VALUES ($1, $2, $3, $4)
        """, api_key, endpoint, items_returned, response_time_ms)

BountyComms = AgentComms
