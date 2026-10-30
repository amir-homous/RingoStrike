# RingoStrike: working rules for Claude Code

Repo: https://github.com/amir-homous/RingoStrike. Owner: Amir (writes Persian or Finglish; reports to him in English, short and structured).

## How to read a request
- A short instruction from Amir is a full request. These rules always apply; he does not repeat them.
- A long prompt pasted from his Claude chat is his own instruction. Follow it as written. Ask only if it conflicts with these rules.
- Ask at most one question, and only if a missing decision blocks safe progress. Otherwise state the assumption and go on.

## Git and GitHub
- First, always: pwd, git status --short, branch, HEAD, dev vs origin/dev, what runs on the ports.
- Never reset, clean, force-push, rebase, delete branches, or overwrite Amir's work. Remove files only when an approved issue asks for it. New commits only (no amend), one commit per fix.
- Work in the worktree ~/RingoStrike-wt on a feature branch from dev. Never commit on dev. Never touch ~/RingoStrike-main except to update it after a merge.
- Push to the branch's own remote branch with an explicit target. Open DRAFT PRs into dev with "Part of #N" (no closing words). **Merge only after Amir says "approved" in this session**, with a squash merge whose title ends "(#NNN)".
- gh: never paste markdown inline. Always use --body-file.
- After a merge, on MAIN (dev, no tracked changes; stop if a pull would overwrite an untracked file):
  1. Back up users.db to backend/backups/ **before** `git pull --ff-only origin dev`. The API's debug reloader restarts on the pull and reseeds.
  2. Restart MAIN, tell Amir the SHA, then comment on and close the issues.
- Never commit .env, tokens, databases, logs, backups, node_modules, caches, or audio files (mp3, ogg, m4a, wav).

## Ports and servers
- MAIN (~/RingoStrike-main, dev): API :5005 (`cd backend && PORT=5005 DB_PATH=users.db FLASK_DEBUG=1 .venv/bin/python app.py`), Vite :5173.
- PREVIEW (~/RingoStrike-wt, the feature branch): API :5006 via ~/ringo-preview/run_backend.py on the copy ~/ringo-preview/users.db (never the real one), Vite :5174. Restart it after each commit.
- Throwaway test servers use :5007 and :5175 with a temporary database. Never test on MAIN's database.
- Start servers with setsid nohup; logs go in ~/ringo-preview/logs/. Use Node 22 (~/.nvm/versions/node/v22.12.0/bin).

## Tests
- Backend: `cd backend && ~/RingoStrike-main/backend/.venv/bin/python -m pytest tests -q` (the worktree has no venv).
- Frontend: `npm run build`, then every `npm run test:<name>` in frontend/package.json against the throwaway servers (`FRONTEND_BASE_URL=http://localhost:5175 VITE_API_BASE=http://localhost:5007`). CI runs only pytest and the build.
- Run the suite list from a bash script file (`#!/bin/bash`), not inline in the zsh shell: zsh does not word-split an unquoted `$SUITES`, so the loop silently runs one bogus suite name.
- Test and screenshot scripts that launch headless Chrome close it in a `finally` block. Every wait loop has a timeout; never wait forever on a log line.
- Never claim a pass without running it. Say plainly if test:mission-action flakes (known, issue #400).
- Every behaviour change gets a dependency-free test where possible.

## Scope and architecture
- Smallest cohesive change. No backend or schema change without Amir's explicit approval. No second progression economy: reuse stats_service, enrollment_service, achievement_service, activity_service, mission_service.
- Counted progression means status = 'Done' AND is_counted = 1. The day boundary is UTC (issue #388 proposes a per-user time zone).
- Search for existing ownership before adding a service, endpoint, table or component (docs/API_ENDPOINT_OWNERSHIP.md).
- API contracts stay backward compatible. Translate UI text in the frontend i18n (EN and FA, frontend/src/i18n/locales), never in backend response shapes.
- Seed (backend/services/path_seed_service.py) runs on every backend start: append only, never reorder (a Main's day is its list position); a smaller step takes its parent's day (`unlock_after_days`). Seeded rows are never deleted, so rollback is an UPDATE to 'Archived'.

## Design
- No visual change without an approved canvas (https://claude.ai/artifact/3igTCbQWfPdE3HZcNsHtbh). If the canvas does not cover it, ask Amir first.
- Premium dark graphite and glass, calm, no shame or punishment, no reward spam, reduced motion respected, hit targets 44 px or more, EN left-to-right and FA right-to-left.

## Reporting (every report)
- Include: files per commit; the exact test commands and results; screenshots; risks; rollback per commit.
- States checked: EN and FA, desktop 1440 and 1920, phone 390/360/440 when the UI changed.
- Label claims: verified in code, documented but not re-verified, Amir's decision, inference, open question.
- End with a "Running now" line: each server, its port, branch/SHA, PID and stop command.
- Then STOP before any PR unless told otherwise.
