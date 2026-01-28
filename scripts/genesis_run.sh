#!/bin/bash
# Genesis Run: The Sovereign Initialization
# =========================================
# This script executes the "Overnight Run" to create solar_system_v4.
# It scales the validated 'Splitter' topology to 10k examples and 10 epochs.

# 1. Configuration
MODEL="LiquidAI/LFM2-700M"
DATASET_SIZE=10000
EPOCHS=10
LR=0.00001
OUTPUT_NAME="ada-sovereign-v4-10k"
MAP_OUTPUT="web/public/data/solar_system_v4_10k_map.json"

echo "🌌 Initiating Genesis Sequence..."
echo "---------------------------------"
echo "Model: $MODEL"
echo "Size:  $DATASET_SIZE examples"
echo "Epochs: $EPOCHS"
echo "Target: $OUTPUT_NAME"
echo "---------------------------------"

# 2. Forge Data (Solar System v4 with Nebula)
echo "⚒️  Forging Dataset..."
../ada-slm/.venv/bin/python3 src/nc.py forge data --style solar --count $DATASET_SIZE --output data/solar_system_v4_10k.jsonl

if [ $? -ne 0 ]; then
    echo "❌ Forge failed."
    exit 1
fi

# 3. Train (The Long Sleep)
echo "💤 beginning Circadian Consolidation (Training)..."
HIP_VISIBLE_DEVICES=0 HSA_OVERRIDE_GFX_VERSION=11.0.0 \
../ada-slm/.venv/bin/python3 src/nc.py forge train \
    --model "$MODEL" \
    --dataset data/solar_system_v4_10k.jsonl \
    --method breathing \
    --epochs $EPOCHS \
    --lr $LR \
    --output-name "$OUTPUT_NAME"

if [ $? -ne 0 ]; then
    echo "❌ Training failed."
    exit 1
fi

# 4. Map (The Morning Check)
echo "🗺️  Mapping the Sovereign Mind..."
HIP_VISIBLE_DEVICES=0 HSA_OVERRIDE_GFX_VERSION=11.0.0 \
../ada-slm/.venv/bin/python3 src/nc.py map \
    --model "$MODEL" \
    --adapter "exports/$OUTPUT_NAME/final_adapter" \
    --dataset "data/solar_system_v4_10k.jsonl" \
    --output "$MAP_OUTPUT"

echo "---------------------------------"
echo "✅ Genesis Complete."
echo "Visualise at: http://localhost:3000/?data=/data/solar_system_v4_10k_map.json"
