# Coffee Map

A coffee shop discovery website for finding cafes by district in Taiwan.

## Features

- Search coffee shops by district or current location
- Filter by tags: 讀書、不限時、外帶店、寵物友善、插座、wifi, etc.
- Google Maps rating summaries (high & low review highlights)
- Curated content from coffee award lists and food blog articles

## Quick Start

1. Copy `.env.example` to `.env` and fill in your API keys
2. Install dependencies: `pip install -r requirements.txt`
3. Run the server: `python src/main/python/api/app.py`

## Development Guidelines

- Read `CLAUDE.md` before making any changes
- Never commit `.env` or API keys
- Use `src/main/python/` for all source code
- Commit after each completed feature
