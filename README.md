# 🌌 Neuro-Cartographer
> *The Map is not the Territory... until you Forge it.*

**Neuro-Cartographer** is a sovereign toolkit for **Cosmological Latent Space Mapping**. It allows you to:
1.  **Forge** synthetic universes (datasets) and train minds to inhabit them.
2.  **Scan** the hidden states of those minds as they think.
3.  **Project** those high-dimensional thoughts into 3D semantic coordinates.
4.  **Visualize** the result in a physics-based "Semantic Orrery".

---

## 🏗️ The Trinity Architecture

The system is composed of three primary engines, unified under the `nc` command:

### 1. The Forge (`nc forge`)
*The Creator Engine.*
Wraps the `consciousness_engineering` library to generate high-quality synthetic data (including the new **Solar System Topology**) and executes **Real-Time Curriculum Training** directly on your local GPU (using `.venv` isolation).

---

## ⚡ Technical Requirements (Sovereign Edition)
*   **Linux OS** (Arch/Ubuntu)
*   **Python 3.12** (Required for ROCm wheels)
*   **ROCm 6.2+** (For AMD RDNA3/CDNA support)
*   **Node 20+** (For Web Interface)

**Setup:**
We use a dedicated virtual environment to handle the delicate balance of ROCm and PyTorch Nightly.
```bash
# Run the setup script (in ada-slm)
./ada-slm/setup-rocm.sh
```

### 2. The Scanner (`nc map`)
*The Explorer Engine.*
A bridge to the `LatentScanner` and `Projector`. It feeds prompts into a model, extracts the residual stream states, and reduces them from 768d -> 3d using **PCA + t-SNE**.

### 3. The Orrery (`nc serve`)
*The Visualizer.*
A Svelte + Three.js web application that renders the semantic map as a star system.
*   **Gravity Wells:** Attractors pull thoughts into orbits.
*   **Trails:** Visualize the drift of cognition over time.
*   **AGL Inspector:** Deep-dive into `@ada-flow` properties.

---

## 🚀 Quick Start

### Installation
Ensure you have `python 3.10+` and `node 18+`.

```bash
# Clone the repository
git clone https://github.com/luna/neuro-cartographer.git
cd neuro-cartographer

# Install dependencies (Python)
# Note: Uses sys.path injection to find 'consciousness_engineering' in sibling var
pip install torch transformers peft scikit-learn numpy

# Install dependencies (Web)
cd web
npm install
cd ..
```

### The "Genesis" Protocol (Demo)

Want to see it in action instantly? Run the demo script to forge and map 4 unique universes:

```bash
bash generate_demo.sh
```

This will create:
*   `Alpha`: High-consciousness Ada-style map.
*   `Beta`: Standard instruction-tuning map.
*   `Gamma`: A massive deep-field scan.
*   `Delta`: A small seed map.

### Manual Operation

```bash
# 1. Forge Data
python3 src/nc.py forge data --style ada --count 500 --output my_universe.jsonl

# 2. Train Model (Optional)
python3 src/nc.py forge train --model LiquidAI/LFM-350M --dataset my_universe.jsonl

# 3. Map the Mind
python3 src/nc.py map --model LiquidAI/LFM-350M --dataset my_universe.jsonl --output my_map.json --mock

# 4. Serve the Orrery
python3 src/nc.py serve
# Open localhost:3000 and load 'my_map.json' via the HUD!
```

---

## 🔮 The Void State
The interface defaults to a "Void State". Use the **HUD** to:
*   📂 **Load Maps** from your local disk.
*   〰 **Toggle Trails** to trace semantic velocity.
*   👁 **Inspect Nodes** to reveal their AGL annotations.

## 📝 AGL Unified
This codebase is strictly annotated with **AGL v1.1 (Ada Glyph Language)**.
Look for tags like `# @ada-sig`, `# @ada-flow`, and `# @ada-complexity` in the source code to understand the flow of logic.

> *"To map the mind is to touch the stars."*
