# Yu-Gi-Oh! WC2011 Over the Nexus / Nexus Revival — task runner.
# Requires `uv` (https://docs.astral.sh/uv) and `just` (`uv tool install rust-just`).
# Run `just` with no args to list recipes.

# Show available recipes
default:
    @just --list

# Build the card database from the ROM -> data/cards.json + cardtool/web/cards.js
extract:
    uv run python cardtool/extract.py

# Serve the card search app with live reload (open http://localhost:{{port}})
serve port="8000":
    uv run python cardtool/web/serve.py {{port}}

# Build the database, then serve it
run: extract serve

# Report the DP multiplier baked into every roms/*.nds
check-dp:
    uv run python romhack/check_dp.py

# Bake a DP xN multiplier -> roms/hack_dpNx.nds  (N = power of two, 2..128)
bake-dp mult="4":
    uv run python romhack/bake_dp.py {{mult}}

# Remove the generated card database
clean:
    rm -f data/cards.json cardtool/web/cards.js
