
import json
import numpy as np
import sys
from pathlib import Path

def analyze_evolution(path):
    print(f"📉 Analyzing Evolution: {path}")
    with open(path, 'r') as f:
        data = json.load(f)
        
    frames = data["frames"]
    frames.sort(key=lambda x: x["step"])
    
    print(f"   Frames: {len(frames)}")
    
    # Track Centroids per Phase per Frame
    history = {} # phase -> [ (step, pos), ... ]
    densities = {} # phase -> [ (step, radius), ... ]
    
    phases = ["Sun", "Giant_Coding", "Giant_Logic", "Asteroid_Belt", "The_Void"]
    
    for frame in frames:
        step = frame["step"]
        nodes = frame["nodes"]
        
        # Group by phase
        phase_nodes = {p: [] for p in phases}
        for n in nodes:
            p = n.get("category", "default")
            if p in phase_nodes:
                phase_nodes[p].append(np.array(n["pos"]))
                
        # Compute Stats
        for p in phases:
            points = np.array(phase_nodes[p])
            if len(points) == 0: continue
            
            centroid = points.mean(axis=0)
            # Density = Mean distance to centroid
            dists = np.linalg.norm(points - centroid, axis=1)
            density = dists.mean()
            
            if p not in history: history[p] = []
            if p not in densities: densities[p] = []
            
            history[p].append(centroid)
            densities[p].append(density)
            
    # Report
    print("\n📊 --- EVOLUTION REPORT ---")
    
    # 1. Fusion Distance (Sun to Coding/Logic)
    print("\n🔹 The Fusion Check (Distance from Sun Identity):")
    sun_hist = np.array(history["Sun"])
    
    for p in ["Giant_Coding", "Giant_Logic", "The_Void"]:
        if p not in history: continue
        p_hist = np.array(history[p])
        
        # Dist at start vs end
        dist_start = np.linalg.norm(sun_hist[0] - p_hist[0])
        dist_end = np.linalg.norm(sun_hist[-1] - p_hist[-1])
        
        delta = dist_end - dist_start
        status = "MERGING" if dist_end < dist_start else "DRIFTING"
        
        print(f"   {p.ljust(15)}: Start={dist_start:.2f} -> End={dist_end:.2f} ({status})")

    # 2. Density (Gravitational Collapse)
    print("\n🔹 Gravitational Collapse (Cluster Density):")
    for p in phases:
        if p not in densities: continue
        d_start = densities[p][0]
        d_end = densities[p][-1]
        print(f"   {p.ljust(15)}: Radius {d_start:.2f} -> {d_end:.2f}")
        
if __name__ == "__main__":
    analyze_evolution(sys.argv[1])
