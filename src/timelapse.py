
import argparse
import sys
import json
import torch
import numpy as np
from pathlib import Path
from tqdm import tqdm

# Add ada-slm to path
current_file = Path(__file__).resolve()
workspace_root = current_file.parents[2]
target_path = workspace_root / 'ada-slm'
if str(target_path) not in sys.path:
    sys.path.append(str(target_path))

try:
    from consciousness_engineering.analysis.scanner import LatentScanner
    from projector import Projector, build_system_state
except ImportError as e:
    print(f"❌ Bridge Error: {e}")
    sys.exit(1)

def run_timelapse(args):
    """
    Generate a timelapse of latent space evolution.
    """
    print(f"🎞️  Timelapse Scanner Target: {args.run_dir}")
    
    run_dir = Path(args.run_dir)
    # Usually inside phase_0 if using CurriculumTrainer
    # Check if run_dir itself has checkpoints or subfolder
    checkpoints = sorted(list(run_dir.glob("**/checkpoint-*")), key=lambda p: int(p.name.split('-')[-1]))
    
    if not checkpoints:
        print("❌ No checkpoints found in directory.")
        return

    print(f"   Found {len(checkpoints)} checkpoints.")
    
    # Load Prompts
    from map import load_prompts
    items = load_prompts(args.dataset)
    prompts = [item['label'] for item in items]
    print(f"   Loading {len(prompts)} probes from {args.dataset}")

    # Initialize Scanner
    scanner = LatentScanner(
        model_name_or_path=args.model,
        device=args.device,
        dtype=torch.float16
    )

    frames = []

    # Collect all vectors for global projection if needed
    all_raw_vectors = [] 
    step_indices = []

    # 1. BASELINE
    print(f"\n🚀 Scanning Baseline (Step 0)...")
    vectors, _ = scanner.scan(prompts, batch_size=args.batch_size)
    if args.save_raw:
        all_raw_vectors.append(vectors)
        step_indices.extend([0] * len(vectors))

    # Project Baseline (Local) - Still useful for quick preview
    projector = Projector(method="tsne", perplexity=30)
    coords = projector.project(vectors)
    state = build_system_state(coords, items)
    frames.append({ "step": 0, "nodes": state["nodes"], "attractors": state["attractors"] })

    del scanner
    torch.cuda.empty_cache()

    # 2. CHECKPOINTS
    for ckpt in checkpoints:
        step = int(ckpt.name.split('-')[-1])
        print(f"\n📸 Scanning Checkpoint {step}...")
        
        scanner = LatentScanner(args.model, device=args.device, dtype=torch.float16)
        scanner.load_adapter(str(ckpt))
        
        vectors, _ = scanner.scan(prompts, batch_size=args.batch_size)
        if args.save_raw:
            all_raw_vectors.append(vectors)
            step_indices.extend([step] * len(vectors))
        
        # Local Projection
        projector = Projector(method="tsne", perplexity=30)
        coords = projector.project(vectors)
        state = build_system_state(coords, items)
        frames.append({ "step": step, "nodes": state["nodes"], "attractors": state["attractors"] })
        
        del scanner
        torch.cuda.empty_cache()

    # Save Evolution Timeline (Locally Projected)
    with open(args.output, 'w') as f:
        json.dump({"type": "evolution", "frames": frames}, f, indent=2)
    print(f"\n✨ Local Timeline saved to: {args.output}")

    # Save Raw Vectors (for Global Projection)
    if args.save_raw:
        raw_path = Path(args.output).with_suffix('.npz')
        # Stack all: shape (Total_Steps * N_Prompts, D_Dim)
        # We need to know N_Prompts to reshape later
        stacked_vectors = np.concatenate(all_raw_vectors, axis=0) # (14000, 768)
        
        np.savez_compressed(
            raw_path, 
            vectors=stacked_vectors, 
            steps=np.array(step_indices),
            prompts=prompts
        )
        print(f"💾 Raw Vectors saved to: {raw_path} (Use for Global Projection)")

    
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-dir", required=True, help="Directory containing checkpoints")
    parser.add_argument("--model", required=True, help="Base model name")
    parser.add_argument("--dataset", required=True, help="Probe dataset")
    parser.add_argument("--output", default="evolution.json", help="Output file")
    parser.add_argument("--device", default="cuda")
    parser.add_argument("--batch-size", type=int, default=4)
    parser.add_argument("--save-raw", action="store_true", help="Save raw 768d vectors to npz")
    
    args = parser.parse_args()
    run_timelapse(args)

if __name__ == "__main__":
    main()
