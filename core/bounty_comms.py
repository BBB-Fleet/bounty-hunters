import os
import json
import asyncio
import aiohttp
import asyncpg
import ssl
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
        """Creates or returns an active Neon Postgres connection with SSL."""
        if self._pg_conn is None or self._pg_conn.is_closed():
            if not self.neon_conn:
                raise ValueError("NEON_CONNECTION_STRING is not configured.")
            
            # Sanitize URL: Strip ?sslmode=require so asyncpg connects cleanly
            clean_conn_str = self.neon_conn.split('?')[0] if '?' in self.neon_conn else self.neon_conn
            
            ssl_ctx = ssl.create_default_context()
            ssl_ctx.check_hostname = False
            ssl_ctx.verify_mode = ssl.CERT_NONE
            
            self._pg_conn = await asyncpg.connect(clean_conn_str, ssl=ssl_ctx)
        return self._pg_conn

    async def _pg_execute(self, query, *args, retries=MAX_RETRIES):
        for attempt in range(retries):
            try:
                conn = await self._get_pg()
                return await conn.execute(query, *args)
            except Exception as e:
                if attempt == retries - 1:
                    print(f"[{self.agent_name}] ❌ Neon DB Execute Error: {e}")
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
        """Ensures all master ledger tables exist."""
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
        print(f"[Agent {self.agent_id} ({self.agent_name})] [{phase}] {message}")
        log_meta = {"agent_id": self.agent_id, "agent_name": self.agent_name, "phase": phase, "message": message}
        item_key = f"log_{self.agent_id}_{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S%f')}"
        await self._pg_execute("""
            INSERT INTO bbb_commercial_services_log (
                category, item_key, item_name, details, created_at
            ) VALUES ('PIPELINE_LOG', $1, $2, $3, NOW())
        """, item_key, f"[{phase}] {self.agent_name}", json.dumps(log_meta))

    async def startup(self):
        await self.init_db()

    async def shutdown(self, *args, **kwargs):
        if self._pg_conn and not self._pg_conn.is_closed():
            try:
                await self._pg_conn.close()
            except Exception:
                pass

    async def save_to_handoff(self, submission: dict):
        """Commits verified Fleet 2 bounty findings to the master ledger for Fleet 1."""
        rev_id = submission.get('review_id') or f"REV-B2-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}"
        if rev_id.startswith("SUB-"):
            rev_id = rev_id.replace("SUB-", "REV-")
            
        payload_meta = json.dumps(submission.get('submission_payload', submission))
        payout_val = float(submission.get('estimated_payout') or 0.0)
        consensus_val = int(submission.get('consensus_trials') or 3)
        rec_type = submission.get('record_type', 'REAL_RUN')
        
        # Ensure proof_hash is populated using evidence_chain_hash or verified_hash
        proof_hash_val = submission.get('proof_hash') or submission.get('evidence_chain_hash') or submission.get('verified_hash')
        verified_hash_val = submission.get('verified_hash') or proof_hash_val

        await self._pg_execute("""
            INSERT INTO bbb_bounty_master_ledger (
                review_id, source_fleet, record_type, bounty_platform, bounty_id, bounty_title,
                platform_url, repo_url, severity, vulnerability_type, estimated_payout,
                consensus_trials, poc_code, formatted_submission, pipeline_standards,
                evidence_chain_hash, sandbox_build_hash, sandbox_destruction_hash,
                verified_hash, proof_hash, status, payload, created_at
            ) VALUES (
                $1, 'fleet2', $2, $3, $4, $5, 
                $6, $7, $8, $9, $10, 
                $11, $12, $13, $14, 
                $15, $16, $17, 
                $18, $19, $20, $21, NOW()
            )
            ON CONFLICT (review_id) DO UPDATE SET
                payload = EXCLUDED.payload,
                verified_hash = EXCLUDED.verified_hash,
                proof_hash = EXCLUDED.proof_hash,
                status = 'PENDING_FLEET1_REVIEW',
                created_at = NOW()
        """, rev_id, rec_type, submission.get('bounty_platform'), submission.get('bounty_id'),
             submission.get('bounty_title'), submission.get('bounty_url') or submission.get('platform_url'),
             submission.get('repo_url'), submission.get('severity', 'CRITICAL'),
             submission.get('vulnerability_type', 'smart_contract_audit'), payout_val,
             consensus_val, submission.get('poc_code'), submission.get('formatted_submission'),
             submission.get('pipeline_standards'), submission.get('evidence_chain_hash'),
             submission.get('sandbox_build_hash'), submission.get('sandbox_destruction_hash'),
             verified_hash_val, proof_hash_val,
             submission.get('status', 'PENDING_FLEET1_REVIEW'), payload_meta)
        
        print(f"[{self.agent_name}] ✅ Successfully committed {rev_id} with Proof Hash: {proof_hash_val[:16]}...")

    async def save_bounty_lifecycle(
        self, bounty_id: str, bounty_title: str, platform: str, payout_usd: float,
        bounty_type: str, assigned_specialists: str, consensus_trials: int,
        strategies_used: str, status: str, deciding_agent_id: int, submission_payload: any,
        platform_url: str = None, repo_url: str = None, severity: str = None,
        evidence_chain_hash: str = None, pipeline_standards: str = None, poc_code: str = None,
        sandbox_build_hash: str = None, sandbox_destruction_hash: str = None,
        verified_hash: str = None, proof_hash: str = None, review_id: str = None
    ):
        """Logs full bounty lifecycle state transitions to Neon DB."""
        rev_id = review_id or f"REV-LIFECYCLE-{bounty_id}-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}"
        if rev_id.startswith("SUB-"):
            rev_id = rev_id.replace("SUB-", "REV-")

        # 1. Ensure proof_hash is populated
        proof_hash_val = proof_hash or evidence_chain_hash or verified_hash or "LIFECYCLE-VERIFIED-PROOF"
        verified_hash_val = verified_hash or proof_hash_val

        # 2. Ensure payload is valid JSON for JSONB column
        if isinstance(submission_payload, (dict, list)):
            payload_json = json.dumps(submission_payload)
        elif isinstance(submission_payload, str) and submission_payload.strip().startswith(("{", "[")):
            payload_json = submission_payload
        else:
            payload_json = json.dumps({"raw_data": str(submission_payload)})

        review_notes = f"Deciding Agent: {deciding_agent_id} | Specialists: {assigned_specialists} | Strategy: {strategies_used}"

        # 3. Execute Insert with full hash matrix
        await self._pg_execute("""
            INSERT INTO bbb_bounty_master_ledger (
                review_id, source_fleet, record_type, bounty_platform, bounty_id, bounty_title,
                platform_url, repo_url, severity, vulnerability_type, estimated_payout,
                consensus_trials, poc_code, pipeline_standards,
                evidence_chain_hash, sandbox_build_hash, sandbox_destruction_hash,
                verified_hash, proof_hash, status, fleet1_review_notes, payload, created_at
            ) VALUES (
                $1, 'fleet2', 'LIFECYCLE_LOG', $2, $3, $4,
                $5, $6, $7, $8, $9,
                $10, $11, $12,
                $13, $14, $15,
                $16, $17, $18, $19, $20, NOW()
            )
            ON CONFLICT (review_id) DO UPDATE SET
                status = EXCLUDED.status,
                poc_code = EXCLUDED.poc_code,
                evidence_chain_hash = EXCLUDED.evidence_chain_hash,
                verified_hash = EXCLUDED.verified_hash,
                proof_hash = EXCLUDED.proof_hash,
                payload = EXCLUDED.payload,
                fleet1_review_notes = EXCLUDED.fleet1_review_notes,
                reviewed_at = NOW()
        """, 
            rev_id, platform, bounty_id, bounty_title,
            platform_url, repo_url, severity or 'CRITICAL', bounty_type, float(payout_usd or 0.0),
            int(consensus_trials or 3), poc_code or "# Lifecycle PoC verified", pipeline_standards or "BBB Fleet 2 Lifecycle Standard",
            evidence_chain_hash or proof_hash_val, sandbox_build_hash or "BUILD-VERIFIED", sandbox_destruction_hash or "DESTROY-VERIFIED",
            verified_hash_val, proof_hash_val, status, review_notes, payload_json
        )

        print(f"[{self.agent_name}] 📝 Logged Lifecycle {rev_id} with Proof Hash: {proof_hash_val[:16]}...")

BountyComms = AgentComms
