# Apex Status & Working Agreement

## Purpose

- Single source of truth for Apex architecture, deployment, and current work-in-progress.
- Onboard new contributors and support thread transfers by pointing them here first.

## Core Architecture (Snapshot)

- Frontend: dashboard_v1 (React + Vite) deployed via Vercel. [file:4]
- Backend: FastAPI v2 API on Render, backed by PostgreSQL. [file:4]
- API base: https://apex-backend-i7b0.onrender.com (all new work uses /api/v2/*). [file:4]

## Frontend Status (Dashboard_v1)

- Contact list and ContactDetailPage are wired to the v2 backend and read enrichment from PostgreSQL. [file:15][file:17]
- ContactDetailPage maps enrichment.sections into Overview, Company, Sales Intel, Personality, and Raw tabs.
- Remaining enhancements: richer Sales Intel cards, personality content once backend emits personality_and_communication, and additional pages (Deals, Signals, Analytics).

## Backend Status

- v2 contacts API exposes enriched contacts with enrichment.version, metadata, and sections JSON. [file:15]
- Enrichment pipeline is populating overview, company_overview, market_position, recent_activity_and_news, leadership_and_culture, pain_points_and_challenges, and budget_and_authority. [file:15]
- Remaining enhancements: add personality_and_communication, opportunity_insights, cadence-related sections, and scoring/signal endpoints to support new Dashboard_v1 views.

## Working Agreement (Keep This Living)

- Every significant architecture or behavior change MUST update:
  - This file (Apex Status & Working Agreement).
  - Any relevant architecture docs (e.g., APEX-ARCHITECTURE*.md, FRONTEND-DEC*.md). [file:4]
- When handing off work or starting a new thread:
  - Link to this file in the first message.
  - Assume GitHub (main branch) is the truth; avoid describing architecture only in chat.
- Before cutting a release or promoting to production:
  - Confirm this document matches the deployed stack (frontend routes, API bases, and critical endpoints).

