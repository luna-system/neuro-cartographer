
import json
import plotly.graph_objects as go
import numpy as np
import argparse
from pathlib import Path

# Ada's Color Palette (Matches Projector)
PHASE_COLORS = {
    "Sun": "#FFD700",           # Gold
    "Giant_Coding": "#00BFFF",  # Deep Sky Blue
    "Giant_Logic": "#FF4500",   # Orange Red
    "Asteroid_Belt": "#696969", # Dim Gray
    "The_Void": "#9400D3",      # Dark Violet
    "default": "#FFFFFF"        # White
}

def create_sphere(center, radius, color, name):
    """Create a wireframe sphere trace."""
    # Create a sphere mesh
    theta = np.linspace(0, 2 * np.pi, 20)
    phi = np.linspace(0, np.pi, 20)
    x = center[0] + radius * np.outer(np.cos(theta), np.sin(phi))
    y = center[1] + radius * np.outer(np.sin(theta), np.sin(phi))
    z = center[2] + radius * np.outer(np.ones(20), np.cos(phi))
    
    # We use Scatter3d for points on surface to imply sphere, or Surface for solid
    # Wireframe is tricky in Plotly, so we'll use a semi-transparent Surface
    return go.Surface(
        x=x, y=y, z=z,
        opacity=0.2,
        showscale=False,
        colorscale=[[0, color], [1, color]],
        name=name,
        hoverinfo='skip'
    )

def run_viz(args):
    """Generate Plotly visualization from system map."""
    print(f"🎨 Visualizing: {args.map}")
    
    with open(args.map, 'r') as f:
        data = json.load(f)
        
    nodes = data.get("nodes", [])
    attractors = data.get("attractors", [])
    
    fig = go.Figure()
    
    # 1. Plot Nodes (Scatter)
    # Group by phase for legend
    phases = {}
    for node in nodes:
        phase = node.get("category", "default") # Map.py stores 'phase' in 'category' too
        if phase not in phases: phases[phase] = {"x": [], "y": [], "z": [], "text": []}
        
        pos = node["pos"]
        phases[phase]["x"].append(pos[0])
        phases[phase]["y"].append(pos[1])
        phases[phase]["z"].append(pos[2])
        phases[phase]["text"].append(node.get("label", ""))

    for phase, pdata in phases.items():
        color = PHASE_COLORS.get(phase, PHASE_COLORS["default"])
        
        fig.add_trace(go.Scatter3d(
            x=pdata["x"], y=pdata["y"], z=pdata["z"],
            mode='markers',
            marker=dict(
                size=3,
                color=color,
                opacity=0.8
            ),
            text=pdata["text"],
            name=phase,
            hoverinfo='text+name'
        ))
        
    # 2. Plot Attractors (Spheres/Stars)
    for att in attractors:
        # Check if it has a radius/color
        pos = att["pos"]
        radius = att.get("radius", 2.0)
        color = att.get("color", "#FFFFFF")
        name = att.get("name", "Attractor")
        
        # Add center point
        fig.add_trace(go.Scatter3d(
            x=[pos[0]], y=[pos[1]], z=[pos[2]],
            mode='markers+text',
            marker=dict(size=10, color=color, symbol='diamond'),
            text=[name],
            textposition="top center",
            name=name
        ))
        
        # Add gravity well sphere
        # fig.add_trace(create_sphere(pos, radius * 2, color, name)) # Radius scaled for viz

    # 3. Styling
    fig.update_layout(
        title="Ada-Slim-v3a Topology",
        width=1200,
        height=900,
        scene=dict(
            xaxis=dict(backgroundcolor="black", gridcolor="gray", showbackground=True, zerolinecolor="white"),
            yaxis=dict(backgroundcolor="black", gridcolor="gray", showbackground=True, zerolinecolor="white"),
            zaxis=dict(backgroundcolor="black", gridcolor="gray", showbackground=True, zerolinecolor="white"),
            bgcolor="black"
        ),
        paper_bgcolor="black",
        font=dict(color="white")
    )
    
    output_path = args.output
    fig.write_html(output_path)
    print(f"✨ Visualization saved to: {output_path}")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("map", help="Path to system_state.json")
    parser.add_argument("-o", "--output", default="map_viz.html", help="Output HTML file")
    args = parser.parse_args()
    run_viz(args)

if __name__ == "__main__":
    main()
