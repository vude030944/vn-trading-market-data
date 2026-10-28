Symbol universes, one UPPERCASE symbol per line. Blank lines and lines beginning
with `#` are ignored.

Generate or refresh them with `scripts/fetch_symbols.py` at the repository root.

Why a file rather than an environment variable: the universe is 1600+ symbols and
changes monthly (new listings, delistings) — editing a file and restarting the
service is cheaper than editing a value inside a secret manager.
