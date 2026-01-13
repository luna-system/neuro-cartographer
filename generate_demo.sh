#!/bin/bash
# generate_demo.sh
# Creates 4 Universes to demonstrate Neuro-Cartographer capabilities.
# @ada-flow: forge → train(dry) → map(mock) → deploy

set -e

echo "🌌 Initializing Galactic Forge Sequence..."
DATA_DIR="./data"
MAP_DIR="./web/public/data"
mkdir -p $DATA_DIR
mkdir -p $MAP_DIR

# --- 1. Universe ALPHA (The Awakening) ---
echo "--- Forging Alpha (Ada Style) ---"
python3 src/nc.py forge data --style ada --count 100 --output $DATA_DIR/alpha.jsonl
python3 src/nc.py forge train --model "LiquidAI/LFM-Alpha" --dataset $DATA_DIR/alpha.jsonl --method breathing --output-name alpha_run
python3 src/nc.py map --model "LiquidAI/LFM-Alpha" --dataset $DATA_DIR/alpha.jsonl --output $MAP_DIR/map_alpha.json --mock

# --- 2. Universe BETA (The Instruction) ---
echo "--- Forging Beta (Standard Style) ---"
python3 src/nc.py forge data --style standard --count 100 --output $DATA_DIR/beta.jsonl
python3 src/nc.py forge train --model "LiquidAI/LFM-Beta" --dataset $DATA_DIR/beta.jsonl --method standard --output-name beta_run
python3 src/nc.py map --model "LiquidAI/LFM-Beta" --dataset $DATA_DIR/beta.jsonl --output $MAP_DIR/map_beta.json --mock

# --- 3. Universe GAMMA (The Deep Field) ---
echo "--- Forging Gamma (Large Ada) ---"
python3 src/nc.py forge data --style ada --count 300 --output $DATA_DIR/gamma.jsonl
python3 src/nc.py map --model "LiquidAI/LFM-Gamma" --dataset $DATA_DIR/gamma.jsonl --output $MAP_DIR/map_gamma.json --mock

# --- 4. Universe DELTA (The Seed) ---
echo "--- Forging Delta (Small Standard) ---"
python3 src/nc.py forge data --style standard --count 50 --output $DATA_DIR/delta.jsonl
python3 src/nc.py map --model "LiquidAI/LFM-Delta" --dataset $DATA_DIR/delta.jsonl --output $MAP_DIR/map_delta.json --mock

echo "✅ All Universes Forged & Mapped."
echo "   Run: nc serve <map_file>"
