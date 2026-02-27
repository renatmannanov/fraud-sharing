# CLAUDE.md — Candidate Verification System

## Communication
- **User communication:** Russian
- **Code comments:** English
- **Commit messages:** English
- **Variable/function names:** English

## Project Overview
System for cross-verifying candidate work experience through hash-based matching.
PII is hashed, never stored in plain text, never returned via API.
See `docs/candidate_verification_system.md` for full technical spec.

## Stack
- Python 3.11+
- FastAPI
- PostgreSQL 15+ (via Docker Compose)
- Alembic (migrations)
- Ollama + DeepSeek R1:14B (schema mapping LLM)
- dateparser (date normalization)

## Quick Reference
| What | Where |
|------|-------|
| Technical spec | `docs/candidate_verification_system.md` |
| Architecture | `docs/ARCHITECTURE.md` |
| API app | `app/main.py` |
| Normalization | `app/core/normalize.py` |
| Hashing | `app/core/fingerprint.py` |
| Matching logic | `app/core/matching.py` |
| DB models | `app/db/models.py` |
| Migrations | `app/db/migrations/` |
| Tests | `tests/` |
| Secrets | `.env` (NEVER commit) |

## Commands
```bash
# Local dev
docker-compose up -d postgres        # start DB
alembic upgrade head                  # run migrations
uvicorn app.main:app --reload         # start API

# Tests
pytest tests/ -v

# Ollama
ollama run deepseek-r1:14b            # check LLM works
```

## Git Workflow
- Never commit directly to `main`
- Use `dev` branch for testing
- Feature branches: `feature/*`, fix branches: `fix/*`
- Test on `dev` before merging to `main`
- Commit messages: concise English, explain "why" not "what"

## Critical Rules

### 1. NO PII in logs, responses, or stored in plain text
- All personal data (name, phone, email, DOB) → hash immediately, discard original
- API responses contain only UUIDs and aggregated facts
- Logs must never contain names, phones, emails in cleartext
- Pepper lives ONLY in env vars, never in code or DB

### 2. Normalize BEFORE hashing
Wrong order = different hashes for same person = broken matching.
```
CORRECT: raw phone → normalize → hash
WRONG:   raw phone → hash ("+7 916..." ≠ "79161234567")
```

### 3. UUID is random, never derived from data
```python
# CORRECT
uid = uuid.uuid4()

# WRONG — client could reverse-engineer
uid = sha256(phone_hash)
```

### 4. Keep directories clean
- Never dump temp/generated files into folder roots — use dedicated subfolders
- `docs/` structure: topic-based subfolders (e.g. `docs/estaff_api/`, `docs/knowledge/`)
- `scripts/` — utility scripts, explorers, one-off tools
- Temp files (PNGs from PDF, intermediate JSON) — delete after use or move to proper subfolder

### 5. Better a duplicate than a false merge
If matching score is low → create new candidate.
Duplicates can be merged later. False merges corrupt data permanently.

## Quality Standards
- Quality > Speed — better less, but better
- Long-term foundation > quick hacks
- Verify after implementation: does the full path work end-to-end?

## Integration Checklist (after new component)
- [ ] Import added where needed
- [ ] Registered (router, handler, model)
- [ ] Called from correct place
- [ ] User action → code path exists
- [ ] Tests cover happy path + edge cases

## Task Tracker (`docs/task_tracker/`)
```
docs/task_tracker/
├── to_do/       # Current plans and tasks — READ FREELY
├── backlog/     # Deferred ideas — READ FREELY
├── done/        # Completed — DO NOT READ without user request
└── archived/    # Obsolete — DO NOT READ without user request
```

### Plan Execution Rules
- Plan file = single source of truth. Execute from file, not from memory
- Execute tasks IN ORDER from the file
- After context compaction → RE-READ the plan file
- If plan > 300 lines → warn user, propose splitting
- After completing a plan, report:
  - ✅ Implemented: [list]
  - ⚠️ Partial: [list with reasons]
  - ❌ Not implemented: [list with reasons]

## Knowledge Base (`docs/knowledge/`)
- `hacks.md` — working solutions, discovered patterns, important findings
- Updated as we go, not retroactively

## Entry Points by Task
| Task | Start here |
|------|-----------|
| New feature | `docs/ARCHITECTURE.md` → plan → implement |
| Bug fix | Logs → affected module → fix → test |
| New data source | Normalization → hashing → matching pipeline |
| Schema change | Alembic migration → models → API |

## First Message Protocol
Before starting work:
1. Confirm understanding of the task
2. List which files will be read/modified
3. Outline execution plan
4. Ask clarifying questions if any
5. Wait for confirmation (unless task is trivial)
