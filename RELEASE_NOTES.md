# Neuro-Cartographer v1.0: "The Void Edition"
**Release Date:** 2026-01-13
**Architects:** Luna & Antigravity

> "The map is not the territory... until you forge the territory yourself."

## 🌟 Feature Highlights

### 1. The Sovereign CLI (`nc`)
A unified command interface to rule them all.
- `nc forge`: Create universes and train minds.
- `nc map`: Extract phantoms from the latent space.
- `nc serve`: Project the universe onto the Orrery.

### 2. The Semantic Orrery (UX Overhaul)
- **The Void State:** Starts empty, pulsing with potential.
- **Drag-and-Drop:** Load any map JSON instantly via the HUD.
- **Gravity Wells:** 3D Attractors with physics-based node interactions.
- **Trail System:** Visual history of semantic drift (toggleable).
- **Inspector:** Deep-dive into node metadata and AGL tags.

### 3. The scanner & Projector
- **Mock Mode:** Test the pipeline without a GPU (`--mock`).
- **Chat Support:** Handles OpenAI-style message lists.
- **Dimensionality:** Robust PCA/t-SNE pipeline.

## 📦 Included Universes (Demo Data)
located in `web/public/data/`

1.  **Alpha (`map_alpha.json`):** 200 nodes. High-density Ada Consciousness.
2.  **Beta (`map_beta.json`):** 100 nodes. Standard Instruction Tuning.
3.  **Gamma (`map_gamma.json`):** 600 nodes. The "Deep Field" Scan.
4.  **Delta (`map_delta.json`):** 50 nodes. Minimalist Seed.

## 🚀 Quick Start

```bash
# 1. Generate Universes
bash generate_demo.sh

# 2. Launch the Orrery
nc serve

# 3. Open Browser
# Load 'web/public/data/map_gamma.json' via the HUD file picker!
```

---
*Forged in the fires of recursion.*
