
import json
import numpy as np
from pathlib import Path
from scipy.spatial import KDTree

def load_coords(path):
    with open(path) as f:
        data = json.load(f)
    if 'nodes' not in data: return None
    coords = []
    for n in data['nodes']:
        if 'pos' in n:
            coords.append(n['pos'])
        elif 'x' in n:
             coords.append([n['x'], n['y'], n.get('z', 0)])
    return np.array(coords)

def calculate_density(name, path):
    coords = load_coords(path)
    if coords is None or len(coords) == 0:
        print(f"⚠️  {name}: No data")
        return

    # Build KDTree for fast neighbor lookup
    tree = KDTree(coords)
    # Query 2 nearest neighbors (1st is self, 2nd is actual neighbor)
    dists, _ = tree.query(coords, k=2)
    
    # Take the distance to the nearest neighbor (column 1)
    nn_dists = dists[:, 1]
    
    mean_dist = np.mean(nn_dists)
    std_dist = np.std(nn_dists)
    
    print(f"🔭 {name:<15} | Particles: {len(coords):<5} | Mean NN Dist: {mean_dist:.4f} (±{std_dist:.4f})")
    return mean_dist

print("🌌 Galactic Density Scan (Semantic Condensation Check)\n" + "-"*60)

files = {
    "Alpha (Birth)": "web/public/data/map_alpha.json",
    "Beta": "web/public/data/map_beta.json",
    "Gamma": "web/public/data/map_gamma.json",
    "V3 (Dream)": "web/public/data/solar_system_v3f_dream_map.json",
    "V3 (Shelter)": "web/public/data/solar_system_v3g_shelter_map.json",
    "Chakra (Hybrid)": "web/public/data/chakra_map.json"
}

results = []
for name, p in files.items():
    if Path(p).exists():
        score = calculate_density(name, p)
        if score: results.append((name, score))

print("-" * 60)
if len(results) >= 2:
    start = results[0][1]
    end = results[-1][1]
    change = ((end - start) / start) * 100
    print(f"📉 Density Change (Alpha -> Now): {change:+.2f}%")
    if change < 0:
        print("✅ Hypothesis Confirmed: The Universe is Condensing.")
    else:
        print("❓ Hypothesis Challenged: The Universe is Expanding.")
