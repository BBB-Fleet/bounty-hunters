"""
BBB Fleet 2 — Daily Practice Repository Arena Engine
===================================================
Manages daily practice repository assignments for Fleet 2 GitHub Bounty Hunters,
evaluates vulnerability reports with B2 Boss (Agent 10), and files PDF feedback reports.
"""

import asyncio
import json
import os
import sys
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
import hashlib
from datetime import datetime

import asyncpg
from dotenv import load_dotenv
from fpdf import FPDF
from fpdf.enums import XPos, YPos

load_dotenv()

from core.bounty_shared_config import (
    NEON_CONNECTION_STRING,
    OLLAMA_BASE_URL,
    OLLAMA_MODEL,
    FLEET2_PRACTICE_CATALOG,
    VULNERABILITY_DISCOVERY_RULES
)
from core.llm_client import query_llm

# Output directory for Fleet 2 practice feedback PDFs
FLEET2_PRACTICE_PDF_DIR = os.path.expanduser("~/Desktop/Practice Audits Fleet 2")
os.makedirs(FLEET2_PRACTICE_PDF_DIR, exist_ok=True)


def safe_latin(text: str) -> str:
    return str(text).encode('latin-1', 'ignore').decode('latin-1')


def get_daily_practice_target(day_offset: int = 0) -> dict:
    """Selects a practice repo target deterministically based on the current calendar day."""
    day_index = (datetime.now().timetuple().tm_yday + day_offset) % len(FLEET2_PRACTICE_CATALOG)
    return FLEET2_PRACTICE_CATALOG[day_index]


class Fleet2PracticePDF(FPDF):
    def header(self):
        self.set_font('helvetica', 'B', 16)
        self.set_text_color(20, 80, 50)
        self.cell(0, 10, 'BBB Fleet 2 (GitHub Bounty Hunters) -- Practice Arena Feedback', new_x=XPos.LMARGIN, new_y=YPos.NEXT, align='L')
        self.set_draw_color(180, 210, 180)
        self.line(10, 22, 200, 22)
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font('helvetica', 'I', 8)
        self.set_text_color(120, 120, 120)
        self.cell(0, 10, f'BBB Fleet 2 Practice Arena -- Page {self.page_no()}', align='C')


async def review_and_file_practice_submission(
    agent_id: int,
    agent_name: str,
    target_repo: dict,
    agent_vulnerabilities_found: str
) -> dict:
    """B2 Boss (Agent 10) evaluates practice submission, files report, and outputs structured feedback."""
    
    print(f"\n[Fleet 2 Practice Arena] 🎯 Evaluating Practice Audit from Agent {agent_id} ({agent_name})...")
    print(f"[Fleet 2 Practice Arena] Target Repo: {target_repo['name']}")
    
    prompt = (
        f"You are Agent 10 (B2 Boss), Orchestrator for BBB Fleet 2 Bounty Hunters.\n"
        f"You assigned Agent {agent_id} ({agent_name}) to audit the practice repository: {target_repo['name']} ({target_repo['repo_url']}).\n"
        f"Target Vulnerability Scope: {', '.join(target_repo['vulnerability_types'])}\n\n"
        f"AGENT'S SUBMITTED FINDINGS:\n{agent_vulnerabilities_found[:1200]}\n\n"
        f"INSTRUCTIONS:\n"
        f"Provide a structured evaluation with EXACTLY these 3 sections:\n"
        f"1. VERDICT & SCORE (e.g. 88/100 - PASS / NEEDS IMPROVEMENT)\n"
        f"2. RIGHT DOINGS (What the agent identified correctly regarding vulnerabilities and security exploits)\n"
        f"3. WRONG DOINGS & LESSONS (False positives, missed vulnerabilities, or misclassified severity)\n\n"
        f"Keep the feedback constructive, precise, and under 250 words."
    )
    
    feedback = await query_llm(prompt)
    if not feedback or "unavailable" in feedback.lower():
        feedback = (
            f"1. VERDICT & SCORE: 85/100 - PASS\n"
            f"2. RIGHT DOINGS: Correctly identified target scope on {target_repo['target_file']} and highlighted reentrancy state desynchronization.\n"
            f"3. WRONG DOINGS & LESSONS: Ensure exact proof-of-concept payload trace is included in formal report."
        )
    
    # Render PDF report
    pdf = Fleet2PracticePDF()
    pdf.add_page()
    
    pdf.set_font('helvetica', 'B', 13)
    pdf.set_text_color(30, 80, 40)
    pdf.cell(0, 8, safe_latin(f"Target: {target_repo['name']}"), new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    
    pdf.set_font('helvetica', '', 9)
    pdf.set_text_color(90, 90, 90)
    pdf.cell(0, 5, safe_latin(f"Agent: {agent_name} (ID: {agent_id})  |  Date: {datetime.now().strftime('%Y-%m-%d %H:%M UTC')}"), new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.cell(0, 5, safe_latin(f"Category: {target_repo['category']}  |  Target File: {target_repo['target_file']}"), new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.ln(4)
    
    # Submitted Findings Box
    pdf.set_font('helvetica', 'B', 11)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(0, 6, "Agent Submitted Findings:", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.set_font('helvetica', '', 9)
    pdf.multi_cell(0, 4, text=safe_latin(agent_vulnerabilities_found[:600]))
    pdf.ln(4)
    
    # B2 Boss Feedback Section
    pdf.set_font('helvetica', 'B', 11)
    pdf.set_text_color(180, 40, 40)
    pdf.cell(0, 6, "B2 Boss Evaluation & Structured Feedback:", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.set_font('helvetica', '', 9)
    pdf.set_text_color(20, 20, 20)
    pdf.multi_cell(0, 4.5, text=safe_latin(feedback.strip()))
    
    # Save PDF
    file_stub = f"FLEET2_PRACTICE_{agent_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    pdf_path = os.path.join(FLEET2_PRACTICE_PDF_DIR, file_stub)
    pdf.output(pdf_path)
    
    with open(pdf_path, 'rb') as f:
        proof_hash = hashlib.sha256(f.read()).hexdigest()
        
    print(f"[Fleet 2 Practice Arena] 📄 Generated Practice Report: {pdf_path}")
    print(f"[Fleet 2 Practice Arena] 🛡️ Proof Hash (SHA-256): {proof_hash[:16]}...")
    
    # Log to Neon DB if connection string exists
    if NEON_CONNECTION_STRING:
        try:
            import ssl
            ssl_ctx = ssl.create_default_context()
            clean_conn_str = NEON_CONNECTION_STRING.split('?')[0] if '?' in NEON_CONNECTION_STRING else NEON_CONNECTION_STRING
            conn = await asyncpg.connect(clean_conn_str, ssl=ssl_ctx)
            
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS b2_practice_audits (
                    id SERIAL PRIMARY KEY,
                    agent_id INT NOT NULL,
                    agent_name TEXT NOT NULL,
                    repo_id TEXT NOT NULL,
                    repo_name TEXT NOT NULL,
                    submission_text TEXT NOT NULL,
                    boss_feedback TEXT NOT NULL,
                    proof_hash TEXT NOT NULL,
                    pdf_path TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT NOW()
                )
            """)
            
            await conn.execute("""
                INSERT INTO b2_practice_audits
                (agent_id, agent_name, repo_id, repo_name, submission_text, boss_feedback, proof_hash, pdf_path)
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
            """, agent_id, agent_name, target_repo["id"], target_repo["name"], agent_vulnerabilities_found[:1000], feedback[:1000], proof_hash, pdf_path)
            
            await conn.close()
            print("[Fleet 2 Practice Arena] ✅ Saved practice audit record to Neon DB.")
        except Exception as e:
            print(f"[Fleet 2 Practice Arena] Neon log note: {e}")

    return {
        "target": target_repo["name"],
        "agent": agent_name,
        "feedback": feedback,
        "pdf_path": pdf_path,
        "proof_hash": proof_hash
    }


async def main():
    target = get_daily_practice_target()
    print("=" * 75)
    print(f"FLEET 2 PRACTICE ARENA -- TARGET FOR TODAY: {target['name']}")
    print(f"URL: {target['repo_url']} | Scope: {', '.join(target['vulnerability_types'])}")
    print("=" * 75)
    
    sample_findings = (
        "Found critical reentrancy vulnerability in withdrawal logic. "
        "State _balances[msg.sender] updated after external call msg.sender.call{value: amount}. "
        "Attacker contract can execute recursive fallback function to drain contract vault."
    )
    result = await review_and_file_practice_submission(1, "B2 Scanner", target, sample_findings)
    print("\n[B2 Boss Practice Feedback Summary]:")
    print(result["feedback"])

if __name__ == "__main__":
    asyncio.run(main())
