
import json
import plotly.graph_objects as go
import argparse
import numpy as np

# Ada's Color Palette
PHASE_COLORS = {
    "Sun": "#FFD700",           # Gold
    "Giant_Coding": "#00BFFF",  # Deep Sky Blue
    "Giant_Logic": "#FF4500",   # Orange Red
    "Asteroid_Belt": "#696969", # Dim Gray
    "The_Void": "#9400D3",      # Dark Violet
    "default": "#FFFFFF"        # White
}

def run_viz_timelapse(args):
    print(f"🎬 Visualizing Timelapse: {args.evolution}")
    
    with open(args.evolution, 'r') as f:
        data = json.load(f)
        
    frames_data = data["frames"] # list of {step: N, nodes: [], attractors: []}
    
    # Sort by step
    frames_data.sort(key=lambda x: x["step"])
    
    steps = [f["step"] for f in frames_data]
    print(f"   Found {len(steps)} frames: {steps}")
    
    # Create the Base Figure (First Frame)
    first_frame = frames_data[0]
    
    # Helper to get trace data for a frame
    def get_traces(frame):
        nodes = frame["nodes"]
        attractors = frame["attractors"]
        
        traces = []
        
        # Group nodes by phase
        phases = {}
        for node in nodes:
            phase = node.get("category", "default")
            if phase not in phases: phases[phase] = {"x": [], "y": [], "z": [], "text": []}
            pos = node["pos"]
            phases[phase]["x"].append(pos[0])
            phases[phase]["y"].append(pos[1])
            phases[phase]["z"].append(pos[2])
            phases[phase]["text"].append(node.get("label", ""))
            
        # Add Node Traces
        # We need a stable order of phases for the animation logic to work (trace indices match)
        # So we iterate through specific keys
        stable_phases = ["Sun", "Giant_Coding", "Giant_Logic", "Asteroid_Belt", "The_Void", "default"]
        
        for p in stable_phases:
            if p in phases:
                pdata = phases[p]
                traces.append(go.Scatter3d(
                    x=pdata["x"], y=pdata["y"], z=pdata["z"],
                    mode='markers',
                    marker=dict(size=3, color=PHASE_COLORS.get(p, "white"), opacity=0.8),
                    text=pdata["text"],
                    name=p
                ))
            else:
                # Add empty trace to keep index alignment?
                # Plotly animation matches frames by trace index or name. 
                # Name matching is safer.
                traces.append(go.Scatter3d(x=[], y=[], z=[], name=p, mode='markers'))

        # Add Attractor Traces (as one trace or multiple?)
        # Let's do one trace for all attractors to simplify
        att_x, att_y, att_z, att_text, att_color = [], [], [], [], []
        for att in attractors:
            pos = att["pos"]
            att_x.append(pos[0])
            att_y.append(pos[1])
            att_z.append(pos[2])
            att_text.append(att.get("name", "Attractor"))
            att_color.append(att.get("color", "white"))
            
        traces.append(go.Scatter3d(
            x=att_x, y=att_y, z=att_z,
            mode='markers+text',
            marker=dict(size=10, color=att_color, symbol='diamond'),
            text=att_text,
            name="Attractors"
        ))
        
        return traces

    # Initialize Figure with Frame 0
    initial_traces = get_traces(first_frame)
    fig = go.Figure(data=initial_traces)
    
    # Create Frames
    plotly_frames = []
    for f_data in frames_data:
        step = f_data["step"]
        traces = get_traces(f_data)
        plotly_frames.append(go.Frame(data=traces, name=str(step)))
        
    fig.frames = plotly_frames
    
    # Layout with Slider and Play Button
    fig.update_layout(
        title="Ada-Slim-v3b Evolution (Solar System)",
        width=1200, height=900,
        scene=dict(
            xaxis=dict(range=[-60, 60], backgroundcolor="black"),
            yaxis=dict(range=[-60, 60], backgroundcolor="black"),
            zaxis=dict(range=[-60, 60], backgroundcolor="black"),
            bgcolor="black"
        ),
        paper_bgcolor="black",
        font=dict(color="white"),
        updatemenus=[{
            "type": "buttons",
            "buttons": [{
                "label": "▶ Play",
                "method": "animate",
                "args": [None, {"frame": {"duration": 500, "redraw": True}, "fromcurrent": True}]
            }, {
                "label": "⏸ Pause",
                "method": "animate",
                "args": [[], {"frame": {"duration": 0, "redraw": False}, "mode": "immediate"}]
            }]
        }],
        sliders=[{
            "steps": [
                {
                    "method": "animate",
                    "args": [[str(s)], {"mode": "immediate", "frame": {"duration": 300, "redraw": True}}],
                    "label": str(s)
                } for s in steps
            ]
        }]
    )
    
    fig.write_html(args.output)
    print(f"✨ Time-Lapse saved to: {args.output}")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("evolution", help="evolution.json file from scanner")
    parser.add_argument("-o", "--output", default="evolution_viz.html")
    args = parser.parse_args()
    run_viz_timelapse(args)

if __name__ == "__main__":
    main()
