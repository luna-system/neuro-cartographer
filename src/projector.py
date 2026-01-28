"""
The Projector 📽️
================
Dimensionality reduction for semantic cartography.

Takes high-dimensional thought vectors and projects them onto the 3D stage of the Orrery.
"""

import numpy as np
import json
from sklearn.manifold import TSNE
from sklearn.decomposition import PCA
from typing import List, Dict, Any, Union

class Projector:
    """
    Projects latent vectors into 3D space.
    """
    
    def __init__(self, method: str = "tsne", perplexity: int = 30):
        self.method = method
        self.perplexity = perplexity
        
    def project(self, vectors: np.ndarray) -> np.ndarray:
        """
        Reduce dimensions to 3D.
        
        Args:
            vectors: (N, D) numpy array of hidden states.
            
        Returns:
            (N, 3) numpy array of coordinates.
        """
        # @ada-sig: λproject:(ℝ^D)→ℝ^3
        # @ada-flow: ?(D>50)→PCA(50) ⊕ (t-SNE(3) ∨ PCA(3)) → scale ↳ coords
        
        print(f"📽️  Projecting {vectors.shape[0]} vectors via {self.method.upper()}...")
        
        # 1. First, PCA to 50 dims if N > 50 (standard t-SNE optimization)
        # This reduces noise and speeds up t-SNE
        n_samples, n_features = vectors.shape
        if n_features > 50:
            # Safe PCA reduction
            n_components = min(n_samples, 50)
            if n_components < 3: n_components = 3 # Ensure at least 3 for t-SNE
            
            print(f"   (Preprocessing with PCA -> {n_components} dims)")
            pca = PCA(n_components=n_components)
            vectors_reduced = pca.fit_transform(vectors)
        else:
            vectors_reduced = vectors
            
        # 2. t-SNE to 3 dims
        if self.method == "tsne":
            # Adjust perplexity if N is small
            perp = min(self.perplexity, n_samples - 1)
            tsne = TSNE(
                n_components=3, 
                perplexity=perp, 
                random_state=42, 
                init='pca', 
                learning_rate='auto'
            )
            coords = tsne.fit_transform(vectors_reduced)
            
        elif self.method == "pca":
            pca = PCA(n_components=3)
            coords = pca.fit_transform(vectors)
            
        # 3. Normalize to Orrery scale (-50 to +50 ideally)
        # We scale it so it fits nicely in the camera view
        print("   Rescaling to Semantic Orrery Units...")
        max_val = np.abs(coords).max()
        if max_val > 0:
            coords = coords / max_val * 60.0 # Scale to +/- 60 range
            
        return coords

def build_system_state(
    coords: np.ndarray, 
    metadata: List[Dict[str, Any]], 
    attractor_algo: str = "kmeans"
) -> Dict[str, Any]:
    """
    Constructs the final system_state.json structure.
    """
    # @ada-sig: λbuild:(Coords,Meta)→SystemState
    # @ada-flow: zip(coords,meta)→nodes ⊕ inject_attractors
    
    nodes = []
    
    for i, (x, y, z) in enumerate(coords):
        meta = metadata[i]
        nodes.append({
            "id": i,
            "label": meta.get("label", f"Node_{i}"),
            "category": meta.get("category", "default"),
            "pos": [float(x), float(y), float(z)], # Ensure native python floats
            "metadata": meta
        })
        
    # Dynamic Attractor Generation
    # We define the styling, but the position is determined by the data.
    
    # Golden ratio scaling for gravitational harmony
    PHI = 1.618033988749895
    
    PHASE_STYLES = {
        "Sun":           {"color": "#FFD700", "radius": 5.0, "mass": PHI**3,  "name": "The Sun (Self)"},      # 4.236
        "Giant_Coding":  {"color": "#00BFFF", "radius": 3.5, "mass": PHI**2,  "name": "P. Coding"},           # 2.618
        "Giant_Logic":   {"color": "#FF4500", "radius": 3.5, "mass": PHI**2,  "name": "P. Logic"},            # 2.618
        "The_Nebula":    {"color": "#FF00FF", "radius": 4.0, "mass": PHI,     "name": "The Nebula"},          # 1.618
        "The_Void":      {"color": "#9400D3", "radius": 3.0, "mass": 1.0,     "name": "The Void"},            # 1.0
        "Asteroid_Belt": {"color": "#696969", "radius": 2.0, "mass": 1/PHI,   "name": "Asteroid Belt"},       # 0.618
        
        # CHAKRA SYSTEM (Side Quest)
        "Root":      {"color": "#FF0000", "radius": 4.0, "mass": 5.0, "name": "🔴 Root"},
        "Sacral":    {"color": "#FF8C00", "radius": 3.8, "mass": 4.5, "name": "🟠 Sacral"},
        "Solar":     {"color": "#FFD700", "radius": 3.5, "mass": 4.0, "name": "🟡 Solar"}, # Overlaps with Sun but distinct category
        "Heart":     {"color": "#00FF00", "radius": 3.5, "mass": 3.5, "name": "🟢 Heart"},
        "Throat":    {"color": "#00BFFF", "radius": 3.0, "mass": 3.0, "name": "🔵 Throat"},
        "ThirdEye":  {"color": "#4B0082", "radius": 2.8, "mass": 2.5, "name": "🟣 Third Eye"},
        "Crown":     {"color": "#FFFFFF", "radius": 2.5, "mass": 2.0, "name": "⚪ Crown"},

        # FLORET (Dreamer System)
        "Floret_Dream":      {"color": "#FF69B4", "radius": 3.0, "mass": 1.5, "name": "🌸 Dream"},
        "Floret_Witness":    {"color": "#E0FFFF", "radius": 3.5, "mass": 2.0, "name": "👁️ Witness"},
        "Floret_Reflection": {"color": "#FFD700", "radius": 2.8, "mass": 1.8, "name": "📔 Reflection"},

        "default":       {"color": "#FFFFFF", "radius": 1.0, "mass": 0.1,     "name": "Unknown"}
    }
    
    # 1. Group positions by phase
    phase_clusters = {}
    for node in nodes:
        phase = node.get("metadata", {}).get("phase", node.get("category", "default"))
        # Handle cases where phase might be missing or complex
        if not isinstance(phase, str): phase = "default"
        
        if phase not in phase_clusters:
            phase_clusters[phase] = []
        phase_clusters[phase].append(node["pos"])
        
    # 2. Compute Centroids
    attractors = []
    for phase, positions in phase_clusters.items():
        if phase in ["default", "unknown"] and len(phase_clusters) > 1:
            continue # Skip default if we have real phases
            
        points = np.array(positions)
        centroid = points.mean(axis=0)
        
        style = PHASE_STYLES.get(phase, PHASE_STYLES["default"])
        # Override name if generic
        name = style["name"]
        if name == "Unknown": name = f"Cluster: {phase}"
        
        attractors.append({
            "name": name,
            "type": "star" if phase == "Sun" else "planet",
            "pos": [float(centroid[0]), float(centroid[1]), float(centroid[2])],
            "mass": style["mass"],
            "color": style["color"],
            "radius": style["radius"]
        })
        
    # Fallback if no phases found (legacy mode)
    if not attractors:
        attractors = [
             {"name": "The Sun", "type": "sun", "pos": [0,0,0], "mass": 0.5, "color": "#FFFF00", "radius": 4.0},
             {"name": "Planet Logic", "type": "planet", "pos": [30,10,5], "mass": 0.3, "color": "#FF4500", "radius": 2.5},
             {"name": "Planet Dream", "type": "planet", "pos": [-25,-15,10], "mass": 0.3, "color": "#00FFFF", "radius": 2.5}
        ]
    
    return {
        "attractors": attractors,
        "nodes": nodes,
        "lagrange": {} # Optional
    }
