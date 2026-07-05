# Yu-Gi-Oh! WC2011 Over the Nexus / Nexus Revival — task runner.
# Requires `uv` (https://docs.astral.sh/uv) and `just` (`uv tool install rust-just`).
# Run `just` with no args to list recipes.

# Show available recipes
default:
    @just --list

# Build the card database from the ROM -> data/cards.json + cardtool/web/public/
extract:
    uv run python cardtool/extract.py

# Install the web app's npm dependencies (run once)
web-install:
    npm --prefix cardtool/web install

# Serve the card search app with Vite HMR (http://localhost:5173)
web-dev:
    npm --prefix cardtool/web run dev

# Build the web app for production (-> cardtool/web/dist)
web-build:
    npm --prefix cardtool/web run build

# Preview the production build (http://localhost:4173)
web-preview:
    npm --prefix cardtool/web run preview

# Build the database, then serve it with Vite HMR
run: extract web-dev

# Report the DP multiplier baked into every roms/*.nds
check-dp:
    uv run python romhack/check_dp.py

# Bake a DP xN multiplier -> roms/hack_dpNx.nds  (N = power of two, 2..128)
bake-dp mult="4":
    uv run python romhack/bake_dp.py {{mult}}

# Remove the generated card database
clean:
    rm -f data/cards.json cardtool/web/public/cards.json
    rm -rf cardtool/web/public/cardart cardtool/web/public/packs
