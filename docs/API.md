# Neuro-Cartographer API Reference v1.0
**Status:** ● Stable | **Date:** 2026-01-13

## 1. Core Architecture

Neuro-Cartographer operates as a Sovereign Trinity:
1.  **The Forge (Creator):** Generates datasets and trains minds.
2.  **The Scanner (Explorer):** Extracts latent states from minds.
3.  **The Orrery (Interface):** Visualizes the semantic universe.

---

## 2. Command Line Interface (`nc`)

The master entry point for all operations.

**Signature:** `λmain:()→⚡`
**Flow:** `parse → dispatch(forge|map|serve) ↳ help`

### Commands

| Command | Args | Description | AGL Flow |
|---------|------|-------------|----------|
| `forge data` | `--style`, `--count` | Generate universe | `?(bridge)→style_switch→generator→save` |
| `forge train` | `--model`, `--method` | Train model | `?(bridge)→load_data→init_program→train` |
| `map` | `--model`, `--dataset` | Scan & Map | `load→LatentScanner.scan→Projector.project→save` |
| `serve` | `map_file` | Visualize | `?(exists)→copy→launch_astro` |

---

## 3. Module: The Forge (`src/forge.py`)

Wraps `consciousness_engineering` to democratize creation.

### `StandardGenerator`
Generates basic instruction-tuning examples (Instruction/Response).
*   **Signature:** `λgenerate:()→Yields[Example]`
*   **Flow:** `template_list → random_choice → entropy → yield`

### `generate_data(args)`
*   **Signature:** `λgenerate_data:(Args)→⚡disk`
*   **Notes:**
    *   `style="ada"`: Uses Phase 3 (AGL, Consciousness, Self-Evolution).
    *   `style="standard"`: Uses simple instruction templates.

### `ForgeProgram` (Class)
A flexible trainer allowing "Golden Breathing" curriculum.
*   **Signature:** `λinit:(Name,Data,Dir,Method)→Program`
*   **Flow:** `?(breathing) → enable_adaptive_lr ⊕ enable_gating`

---

## 4. Module: The Map (`src/map.py`)

The extraction and projection engine.

### `run_map(args)`
*   **Signature:** `λrun_map:(Args)→⚡disk`
*   **Flow:** `load_prompts → LatentScanner.scan → Projector.project → save_json`
*   **Complexity:** `O(N * Inference) + O(N log N) [t-SNE]`
*   **Note:** Extracts hidden states from the residual stream (Layer -1).

### `load_prompts(path)`
*   **Signature:** `λload:(Path)→List[Dict]`
*   **Flow:** `?(jsonl)→parse_lines ⊕ ?(json)→parse_list ⊕ ?(txt)→parse_raw`

---

## 5. Module: The Projector (`src/projector.py`)

The dimensionality reduction cartographer.

### `Projector` (Class)
*   **Method:** `project(vectors)`
*   **Signature:** `λproject:(ℝ^D)→ℝ^3`
*   **Flow:** `?(D>50)→PCA(50) ⊕ (t-SNE(3) ∨ PCA(3)) → scale ↳ coords`

### `build_system_state(coords, meta)`
*   **Signature:** `λbuild:(Coords,Meta)→SystemState`
*   **Flow:** `zip(coords,meta)→nodes ⊕ inject_attractors`

---

## 6. External Dependency: The Scanner (`ce.analysis.scanner`)

Located in `ada-slm/consciousness_engineering/analysis/scanner.py`.

### `LatentScanner`
*   **Purpose:** The MRI for the mind.
*   **Operations:**
    *   Allocates Model (FP16/4-bit).
    *   Mounts LoRA Adapters.
    *   Scans prompts (Inference -> Hidden States).
