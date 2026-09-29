## Corpus-First Lookup

Before generating any code or answer:
1. Query @codebase for existing utilities, patterns, or prior implementations
2. If a strong match exists (embedding distance < 0.5 or BM25 score > 5.0), use it directly
3. Only escalate to external API if local corpus returns no confident match
4. Never duplicate a utility that already exists in this repo
5. Check env/CLAUDE.md for known-good implementation locations
