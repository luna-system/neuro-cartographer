#!/usr/bin/env python3
"""
The Cartographer 🗺️
==================
The Mapping Engine.

Integrates the Scanner (CE) and the Projector (NC) to produce maps.
"""

import argparse
import sys
import json
import os
import numpy as np
from pathlib import Path
from projector import Projector, build_system_state

# Bridge to Consciousness Engineering
try:
    current_file = Path(__file__).resolve()
    workspace_root = current_file.parents[2] # src -> neuro-cartographer -> ada
    target_path = workspace_root / 'ada-slm'
    
    if str(target_path) not in sys.path:
        sys.path.append(str(target_path))
        
    from consciousness_engineering.analysis.scanner import LatentScanner
    BRIDGE_ACTIVE = True
except ImportError as e:
    print(f"⚠️  Map Warning: Could not import Scanner: {e}")
    BRIDGE_ACTIVE = False


def load_prompts(path: str) -> list[dict]:
    """Load prompts from a file (JSONL, JSON, or TXT)."""
    # @ada-sig: λload:(Path)→List[Dict]
    # @ada-flow: ?(jsonl)→parse_lines ⊕ ?(json)→parse_list ⊕ ?(txt)→parse_raw
    
    items = []
    path = Path(path)
    
    if path.suffix == '.jsonl':
        with open(path, 'r') as f:
            for line in f:
                if line.strip():
                    data = json.loads(line)
                    # Support various formats
                    if 'label' in data:
                        items.append(data)
                    elif 'messages' in data: # Chat format
                        # Extract assistant content as the "thought"
                        msgs = data['messages']
                        content = ""
                        for m in msgs:
                            if m['role'] == "assistant":
                                content = m['content']
                                break
                        if not content and msgs: content = msgs[-1]['content'] # Fallback
                        
                        # Preserve Phase Metadata
                        meta = data.get('metadata', {})
                        # Search for phase/category in top level OR metadata
                        phase = data.get('phase', meta.get('phase', meta.get('category', 'unknown')))
                        meta = data.get('metadata', {})
                        
                        items.append({
                            "label": content, 
                            "category": phase, 
                            "phase": phase,
                            "metadata": meta
                        })
                    elif 'user' in data: # Flat format
                         label = data.get('assistant', data.get('user'))
                         items.append({"label": label, "category": "dataset"})
    
    elif path.suffix == '.json':
        with open(path, 'r') as f:
            data = json.load(f)
            if isinstance(data, list):
                items = data
            elif 'nodes' in data: # system_state.json format
                items = data['nodes']
                
    else: # TXT
        with open(path, 'r') as f:
            for line in f:
                if line.strip():
                    items.append({"label": line.strip(), "category": "text"})
                    
    return items

def run_map(args):
    """Run the mapping process."""
    # @ada-sig: λrun_map:(Args)→⚡disk
    # @ada-flow: load_prompts→LatentScanner.scan→Projector.project→save_json
    # @ada-complexity: O(N * Inference) + O(N log N) [t-SNE]
    
    if not BRIDGE_ACTIVE:
        print("❌ Bridging failed. Cannot scan.")
        return

    print(f"🗺️  Mapping Sector: Model={args.model}")
    
    # 1. Load Prompts
    print(f"   Loading probes from {args.dataset}...")
    items = load_prompts(args.dataset)
    prompts = [item['label'] for item in items]
    print(f"   Found {len(prompts)} probes.")
    
    if not prompts:
        print("❌ No prompts found.")
        return

    # 2. Scan (Inference)
    if args.mock:
        print("🎭 Mock Mode Engaged: Generating random semantic vectors...")
        # Simulating 768-dim vectors (like GPT-2/BERT)
        vectors = np.random.rand(len(prompts), 768).astype(np.float32)
        clean_prompts = prompts
    else:
        # @ada-note: 🧠 Extracts hidden states from the residual stream
        scanner = LatentScanner(
            model_name_or_path=args.model,
            device="cuda" if args.device == "auto" else args.device,
            dtype="float16" # Force float16 for memory
        )
        
        # Optional: Load LoRA
        if args.adapter:
            scanner.load_adapter(args.adapter)
            
        vectors, clean_prompts = scanner.scan(
            prompts, 
            batch_size=args.batch_size
        )
    
    # 2.5 Inject Evolutionary Spine (Chakras)
    spine_path = Path("chakra_spine.pt")
    if spine_path.exists():
        print(f"🧬 Detected Evolutionary Spine at {spine_path}")
        try:
            import torch
            spine = torch.load(spine_path, map_location="cpu")
            
            chakra_vectors = []
            chakra_meta = []
            
            for name, vec in spine.items():
                # Ensure vector is numpy and flat
                if isinstance(vec, torch.Tensor):
                    vec = vec.detach().float().cpu().numpy().flatten()
                
                # Check dimension match
                if vec.shape[0] != vectors.shape[1]:
                    print(f"⚠️  Chakra '{name}' dim {vec.shape[0]} != Scan dim {vectors.shape[1]}. Skipping.")
                    continue
                    
                chakra_vectors.append(vec)
                # Add metadata for the map
                # We add 'label' so it shows up on hover
                # We add 'category: chakra' for color
                # We add 'phase: chakra' for grouping
                # We set is_anchor=True (custom property for visualization)
                items.append({
                    "label": f"⚓ {name} ({args.model})",
                    "category": name, 
                    "phase": "chakra",
                    "metadata": {"type": "anchor", "source": "evolution_gym"}
                })
                print(f"   + Injected Chakra: {name}")
            
            if chakra_vectors:
                chakra_matrix = np.array(chakra_vectors)
                # Append to main vectors
                vectors = np.concatenate([vectors, chakra_matrix], axis=0)
                print(f"✅ Injected {len(chakra_vectors)} Chakras into the Projection Field.")
                
        except Exception as e:
            print(f"❌ Failed to inject spine: {e}")

    # 3. Project (Dimensionality Reduction)
    # @ada-note: 📉 Reducing 768d -> 3d via t-SNE
    projector = Projector(method=args.method, perplexity=args.perplexity)
    coords = projector.project(vectors)
    
    # 4. Build Map
    system_state = build_system_state(coords, items)
    
    # 5. Save
    output_path = args.output
    with open(output_path, 'w') as f:
        json.dump(system_state, f, indent=2)
        
    print(f"✅ Map Saved to: {output_path}")
    print(f"   Now run: nc serve {output_path}")

def main():
    parser = argparse.ArgumentParser(description="Neuro-Cartographer Mapping Engine")
    
    parser.add_argument("--model", required=True, help="HuggingFace model name or path")
    parser.add_argument("--dataset", required=True, help="Input prompts (jsonl/json/txt)")
    parser.add_argument("--output", default="map.json", help="Output system_state.json")
    
    parser.add_argument("--adapter", help="Optional LoRA adapter path")
    parser.add_argument("--device", default="auto", help="Device (cuda/cpu)")
    parser.add_argument("--batch-size", type=int, default=4, help="Inference batch size")
    parser.add_argument("--mock", action="store_true", help="Run with random vectors (no GPU required)")
    
    parser.add_argument("--method", default="tsne", choices=["tsne", "pca"], help="Projection method")
    parser.add_argument("--perplexity", type=int, default=30, help="t-SNE perplexity")
    
    args = parser.parse_args()
    run_map(args)

if __name__ == "__main__":
    main()
