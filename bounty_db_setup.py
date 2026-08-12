import os
import asyncio
import asyncpg
from dotenv import load_dotenv

load_dotenv()

NEON_CONNECTION_STRING = os.environ.get('NEON_CONNECTION_STRING')

async def setup_db():
    print("Connecting to Neon DB...")
    conn = await asyncpg.connect(NEON_CONNECTION_STRING)
    
    print("Creating bbb_commercial_services_log table...")
    await conn.execute("""
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
    print("Created bbb_commercial_services_log.")

    print("Creating bbb_bounty_master_ledger table...")
    await conn.execute("""
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
    print("Created bbb_bounty_master_ledger.")

    await conn.close()
    print("Database setup complete.")

if __name__ == "__main__":
    asyncio.run(setup_db())
