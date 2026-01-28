
import numpy as np
import plotly.graph_objects as go
import argparse
import sys
from pathlib import Path

# Add project path for Projector import
current_file = Path(__file__).resolve()
workspace_root = current_file.parents[2]
target_path = workspace_root / 'ada-slm'
if str(target_path) not in sys.path:
    sys.path.append(str(target_path))

from projector import Projector

PHASE_COLORS = {
    "Sun": "#FFD700",           # Gold
    "Giant_Coding": "#00BFFF",  # Deep Sky Blue
    "Giant_Logic": "#FF4500",   # Orange Red
    "Asteroid_Belt": "#696969", # Dim Gray
    "The_Void": "#9400D3",      # Dark Violet
    "default": "#FFFFFF"        # White
}

def run_viz_trajectories(args):
    print(f"📉 Generating Trajectories from: {args.input}")
    
    # 1. Load Raw Vectors
    data = np.load(args.input)
    vectors = data['vectors'] # (TotalN, 768)
    steps = data['steps']     # (TotalN,)
    prompts = data['prompts'] # (1000,)
    
    n_prompts = len(prompts)
    n_steps = len(np.unique(steps))
    print(f"   Loaded {vectors.shape[0]} vectors ({n_steps} steps x {n_prompts} prompts).")
    
    # 2. Global Projection
    print("   Running Global Projection (t-SNE on history)...")
    projector = Projector(method="tsne", perplexity=30)
    # This might take a moment
    coords_flat = projector.project(vectors) # (TotalN, 3)
    
    # 3. Reshape to (Steps, Prompts, 3)
    # We assume the vectors are ordered by step, then by prompt (as written by timelapse.py)
    # To be safe, we can use the 'steps' array, but the chunking should be consistent.
    
    # Let's organize data by PROMPT INDIVIDUALLY to draw lines.
    # prompt_lines = [ { "x": [], "y": [], "z": [], "phase": "Sun" }, ... ]
    
    # Need to classify prompts into phases again (since npz didn't save metadata, just text)
    # We can perform a quick heuristic or pass metadata file.
    # Actually, simpler: load the dataset again or just guess from text (hacky).
    # BETTER: Load prompts using map.load_prompts to get phase!
    
    from map import load_prompts
    # We need the dataset path... or we can infer phase from Prompt text if simple?
    # No, prompts are long. 
    # Let's require dataset argument.
    
    items = load_prompts(args.dataset)
    # Build lookup
    prompt_meta = { item['label']: item for item in items }
    
    traces = []
    
    # Iterate over prompts (0 to 999)
    # For each prompt, extract its 15 coordinates
    
    # coords_flat is shaped (Step0_P0...Step0_P999, Step1_P0...Step1_P999, ...)
    coords_reshaped = coords_flat.reshape(n_steps, n_prompts, 3) 
    # Shape: [Step, Prompt, Dim]
    
    # We want [Prompt, Step, Dim] for plotting lines
    coords_per_prompt = coords_reshaped.transpose(1, 0, 2)
    # Shape: [Prompt, Step, Dim]
    
    print("   Building Traces...")
    
    # Downsample for visualization if too messy? 1000 lines is a lot.
    # Let's plot only 10% or just plot all but thin lines.
    limit = args.limit if args.limit > 0 else n_prompts
    
    for i in range(limit):
        prompt_text = prompts[i] # This might be raw text
        # Lookup metadata
        meta = prompt_meta.get(prompt_text, {})
        phase = meta.get("category", "default")
        
        c = coords_per_prompt[i] # (15, 3)
        
        x = c[:, 0]
        y = c[:, 1]
        z = c[:, 2]
        
        color = PHASE_COLORS.get(phase, "white")
        
        # Line Trace
        traces.append(go.Scatter3d(
            x=x, y=y, z=z,
            mode='lines+markers',
            line=dict(color=color, width=2),
            marker=dict(size=3, color=color),
            name=phase,
            legendgroup=phase, # Group legend items
            showlegend=(i == float('inf')), # Don't show legend for every line (too many)
            text=[f"Step {s}: {prompt_text[:50]}..." for s in range(n_steps)],
            hoverinfo='text'
        ))
        
    # Add dummy legend traces
    for p, col in PHASE_COLORS.items():
        traces.append(go.Scatter3d(
            x=[None], y=[None], z=[None],
            mode='lines+markers',
            line=dict(color=col, width=4),
            marker=dict(size=5, color=col),
            name=p,
            legendgroup=p,
            showlegend=True
        ))

    fig = go.Figure(data=traces)
    fig.update_layout(
        title="Ada-Slim-v3b Evolutionary Trajectories (Global t-SNE)",
        width=1200, height=900,
        scene=dict(
            xaxis=dict(backgroundcolor="black"),
            yaxis=dict(backgroundcolor="black"),
            zaxis=dict(backgroundcolor="black"),
            bgcolor="black"
        ),
        paper_bgcolor="black",
        font=dict(color="white")
    )
    
    fig.write_html(args.output)
    print(f"✨ Trajectories saved to: {args.output}")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("input", help="raw_evolution_v2.npz")
    parser.add_argument("--dataset", required=True, help="Original dataset for metadata")
    parser.add_argument("-o", "--output", default="trajectories.html")
    parser.add_argument("--limit", type=int, default=200, help="Downsample lines (default 200 for clarity)")
    args = parser.parse_args()
    run_viz_trajectories(args)

if __name__ == "__main__":
    main()
