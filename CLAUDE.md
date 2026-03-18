# CLAUDE.md - Coffee Map

> **Documentation Version**: 1.0
> **Last Updated**: 2026-03-18
> **Project**: Coffee Map
> **Description**: Coffee shop discovery website with district filtering, tags (讀書、不限時、外帶店, etc.), Google Maps review summaries, and curated article content from external sources.
> **Features**: Google Maps API integration, web scraping, GitHub auto-backup, technical debt prevention

This file provides essential guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 🚨 CRITICAL RULES - READ FIRST

### 🔄 RULE ACKNOWLEDGMENT REQUIRED
> **Before starting ANY task, Claude Code must respond with:**
> "✅ CRITICAL RULES ACKNOWLEDGED - I will follow all prohibitions and requirements listed in CLAUDE.md"

### ❌ ABSOLUTE PROHIBITIONS
- **NEVER** create new files in root directory → use proper module structure
- **NEVER** write output files directly to root directory → use designated output folders
- **NEVER** create documentation files (.md) unless explicitly requested by user
- **NEVER** use git commands with -i flag (interactive mode not supported)
- **NEVER** use `find`, `grep`, `cat`, `head`, `tail`, `ls` commands → use Read, Grep, Glob tools instead
- **NEVER** create duplicate files (manager_v2.py, enhanced_xyz.py, utils_new.js) → ALWAYS extend existing files
- **NEVER** create multiple implementations of same concept → single source of truth
- **NEVER** copy-paste code blocks → extract into shared utilities/functions
- **NEVER** hardcode values that should be configurable → use config files/environment variables
- **NEVER** use naming like enhanced_, improved_, new_, v2_ → extend original files instead

### 📝 MANDATORY REQUIREMENTS
- **COMMIT** after every completed task/phase - no exceptions
- **GITHUB BACKUP** - Push to GitHub after every commit: `git push origin main`
- **USE TASK AGENTS** for all long-running operations (>30 seconds)
- **TODOWRITE** for complex tasks (3+ steps) → parallel agents → git checkpoints → test validation
- **READ FILES FIRST** before editing
- **DEBT PREVENTION** - Before creating new files, check for existing similar functionality to extend
- **SINGLE SOURCE OF TRUTH** - One authoritative implementation per feature/concept

### ⚡ EXECUTION PATTERNS
- **PARALLEL TASK AGENTS** - Launch multiple Task agents simultaneously for maximum efficiency
- **SYSTEMATIC WORKFLOW** - TodoWrite → Parallel agents → Git checkpoints → GitHub backup → Test validation
- **GITHUB BACKUP WORKFLOW** - After every commit: `git push origin main`
- **BACKGROUND PROCESSING** - ONLY Task agents can run true background operations

### 🔍 MANDATORY PRE-TASK COMPLIANCE CHECK
> **STOP: Before starting any task, Claude Code must explicitly verify ALL points:**

**Step 1: Rule Acknowledgment**
- [ ] ✅ I acknowledge all critical rules in CLAUDE.md and will follow them

**Step 2: Task Analysis**
- [ ] Will this create files in root? → If YES, use proper module structure instead
- [ ] Will this take >30 seconds? → If YES, use Task agents not Bash
- [ ] Is this 3+ steps? → If YES, use TodoWrite breakdown first
- [ ] Am I about to use grep/find/cat? → If YES, use proper tools instead

**Step 3: Technical Debt Prevention (MANDATORY SEARCH FIRST)**
- [ ] **SEARCH FIRST**: Use Grep pattern="<functionality>.*<keyword>" to find existing implementations
- [ ] **CHECK EXISTING**: Read any found files to understand current functionality
- [ ] Does similar functionality already exist? → If YES, extend existing code
- [ ] Am I creating a duplicate class/manager? → If YES, consolidate instead
- [ ] Will this create multiple sources of truth? → If YES, redesign approach

**Step 4: Session Management**
- [ ] Is this a long/complex task? → If YES, plan context checkpoints
- [ ] Have I been working >1 hour? → If YES, consider /compact or session break

> **⚠️ DO NOT PROCEED until all checkboxes are explicitly verified**

## 🏗️ PROJECT OVERVIEW

A web application for discovering coffee shops in Taiwan by district. Users can filter by area, browse shops with tags (讀書、不限時、外帶店、寵物友善, etc.), view Google Maps rating summaries, and read curated content from food blogs and award lists.

### 🎯 DEVELOPMENT STATUS
- **Setup**: ✅ Complete
- **Core Features**: In Progress
- **Testing**: Pending
- **Documentation**: Pending

## 🗂️ PROJECT STRUCTURE

```
Coffee map/
├── CLAUDE.md                          # Essential rules for Claude Code
├── README.md                          # Project documentation
├── .gitignore                         # Git ignore patterns
├── src/
│   ├── main/
│   │   ├── python/
│   │   │   ├── core/                  # Core business logic (shop search, filtering)
│   │   │   ├── utils/                 # Utility functions (scrapers, helpers)
│   │   │   ├── models/                # Data models (CoffeeShop, Tag, Review)
│   │   │   ├── services/              # External service integrations
│   │   │   │                          #   - Google Maps API
│   │   │   │                          #   - Web article scrapers
│   │   │   └── api/                   # Backend API endpoints (Flask/FastAPI)
│   │   └── resources/
│   │       ├── config/                # API keys, settings (use .env, never commit secrets)
│   │       └── assets/                # Static assets (icons, images)
│   └── test/
│       ├── unit/                      # Unit tests
│       └── integration/               # Integration tests (API, scraper)
├── docs/                              # Documentation
├── output/                            # Generated output (exports, reports)
└── tools/                             # Dev utilities
```

## 🔑 KEY INTEGRATIONS

- **Google Maps Places API** — Shop search, ratings, reviews, photos
- **Google Maps Embed API** — Map display in frontend
- **Web Scraping** — Coffee award lists, blog articles (BeautifulSoup / requests)
- **Frontend** — HTML/CSS/JS (or templating via Jinja2/Flask)

## 🚀 COMMON COMMANDS

```bash
# Install dependencies
pip install -r requirements.txt

# Run development server
python src/main/python/api/app.py

# Run tests
pytest src/test/

# Push to GitHub
git push origin main
```

## 🚨 TECHNICAL DEBT PREVENTION

### ✅ CORRECT APPROACH:
1. **Search First** — `Grep(pattern="shop.*search", include="*.py")`
2. **Read Existing** — Understand current patterns before adding
3. **Extend** — Add to existing service/model rather than creating parallel files

---

**⚠️ Prevention is better than consolidation - build clean from the start.**
**🎯 Single source of truth. Extend, never duplicate.**
