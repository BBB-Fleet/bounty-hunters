import os
import asyncio
import asyncpg
from dotenv import load_dotenv

load_dotenv()

NEON_CONNECTION_STRING = os.environ.get('NEON_CONNECTION_STRING')

async def setup_db():
    print("Connecting to Neon DB...")
    conn = await asyncpg.connect(NEON_CONNECTION_STRING)
    
    print("Creating bounty_agent_state table...")
    await conn.execute("""
        CREATE TABLE IF NOT EXISTS bounty_agent_state (
            agent_id INT PRIMARY KEY,
            state_data TEXT,
            updated_at TIMESTAMP DEFAULT NOW()
        )
    """)
    print("Created bounty_agent_state.")
    
    print("Creating bounty_daily_summaries table...")
    await conn.execute("""
        CREATE TABLE IF NOT EXISTS bounty_daily_summaries (
            id SERIAL PRIMARY KEY,
            summary TEXT,
            created_at TIMESTAMP DEFAULT NOW()
        )
    """)
    print("Created bounty_daily_summaries.")
    
    print("Creating bounty_pipeline_log table...")
    await conn.execute("""
        CREATE TABLE IF NOT EXISTS bounty_pipeline_log (
            id SERIAL PRIMARY KEY,
            log_data TEXT,
            created_at TIMESTAMP DEFAULT NOW()
        )
    """)
    print("Created bounty_pipeline_log.")
    
    print("Creating bbb_fleet_handoff table...")
    await conn.execute("""
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
    print("Created bbb_fleet_handoff.")
    
    await conn.close()
    print("Database setup complete.")

if __name__ == "__main__":
    asyncio.run(setup_db())
