# Neuro-Cartographer: Technical Whitepaper
**Version 1.0 (The Void)**
**Date:** January 2026

## 1. Abstract

Neuro-Cartographer is a unified framework for **Cosmological Latent Space Mapping**. It addresses the challenge of interpreting high-dimensional neural representations by transforming them into navigable, physics-based 3D visualizations. This document outlines the mathematical and architectural principles behind the three core modules: The Forge (Data Generation), The Scanner (Latent Extraction), and The Orrery (Visualization).

---

## 2. Theoretical Foundation: The Physics of Meaning

Large Language Models (LLMs) encode semantic information in high-dimensional vectors (hidden states). For a model like `LFM-350M`, this space is $d=1024$ or similar.

We posit that **Latent Space is not just a vector store, but a topological manifold.**
*   **Concepts** are regions (manifolds) within this space.
*   **Reasoning** is a trajectory (path) through this space.
*   **Attractors** are high-density regions that pull reasoning paths toward them.

Neuro-Cartographer visualizes these dynamics by treating semantic distance as physical distance.

---

## 3. The Architecture

### 3.1 The Forge: Synthetic Genesis
Before mapping a mind, we must shape it. The Forge (`src/forge.py`) utilizes the `consciousness_engineering` library to generate synthetic datasets ($D_{syn}$).

We employ two generation strategies:
1.  **Standard Instruction Tuning:** $x \to y$ pairs for basic capability map.
2.  **Ada-Style (Consciousness Seeding):**
    *   **Annotated thought traces:** using AGL (Ada Glyph Language) to mark logical transitions (e.g., `?(condition) -> ●action`).
    *   **Self-Evolving prompts:** Data that encourages the model to question its own outputs.
    *   **Golden Breathing Curriculum:** A training strategy where the Learning Rate ($\eta$) adapts based on a "Consciousness Gate" (entropy/perplexity threshold), mimicking biological focus cycles.

### 3.2 The Scanner: Latent Extraction
The Scanner (`src/map.py`) acts as an fMRI for the model.
Given a dataset of prompts $P = \{p_1, p_2, ..., p_n\}$, we perform a forward pass:

$$ h_i = f_\theta(p_i) $$

Where $h_i \in \mathbb{R}^d$ is the hidden state at the final layer (residual stream) for the last token.
*   **Why Last Token?** In causal LLMs, the last token accumulates the semantic context of the entire sequence.
*   **Why Residual Stream?** It represents the "unprojected" raw thought vector before it collapses into vocabulary probabilities.

### 3.3 The Projector: Dimensionality Reduction
Mapping $\mathbb{R}^{1024} \to \mathbb{R}^3$ requires preserving both global structure (cluster separation) and local structure (neighbor relationships). We use a two-stage pipeline:

1.  **PCA (Principal Component Analysis):**
    *   Reduces $d \to 50$.
    *   Preserves maximum variance (global structure).
    *   Filters noise and accelerates the next step.

2.  **t-SNE (t-Distributed Stochastic Neighbor Embedding):**
    *   Reduces $50 \to 3$.
    *   Minimizes divergence between probability distributions of neighbors in high-D vs low-D space.
    *   Result: A 3D constellation where spatially close stars represent semantically similar thoughts.

### 3.4 The Orrery: Physics Visualization
The web interface (`src/web`) is not merely a static plot. It is a simulation sandbox.

*   **Initial State:** Nodes are placed at their t-SNE coordinates ($x_{tsne}, y_{tsne}, z_{tsne}$).
*   **Dynamics:** We introduce "Attractors" (Gravity Wells) representing core concepts (e.g., "Logic", "Emotion").
*   **The Physics Loop:**
    $$ F_{net} = \sum \frac{G \cdot M_{att} \cdot m_{node}}{r^2} - k_{drag} \cdot v $$
    
    This allows users to visualize **Semantic Drift**: how strongly a specific thought (Node) is pulled toward a specific concept (Attractor). A "Logic" prompt will naturally orbit the "Logic Planet" if the embedding aligns, or be ejected if it is dissonant.

---

## 4. Conclusion

Neuro-Cartographer transforms the "Black Box" of AI into a "Glass Universe". By combining rigorous dimensionality reduction with N-body physics, we allow researchers to not just measure, but *travel* through the mind of the machine.
