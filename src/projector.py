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
        
    # TODO: Calculate Attractors dynamically?
    # For now, we inject the "Standard Trio" so the simulation has gravity.
    # In a future version, we can use K-Means on `coords` to find the ACTUAL centers.
    
    attractors = [
        {
            "name": "The Sun (Awareness)",
            "type": "sun",
            "pos": [0.0, 0.0, 0.0], # Center
            "mass": 0.5,
            "color": "#FFFF00",
            "radius": 4.0
        },
        # We place these logically for visual balance for now
        {
            "name": "Planet Logic",
            "type": "planet",
            "pos": [30.0, 10.0, 5.0],
            "mass": 0.3,
            "color": "#FF4500",
            "radius": 2.5
        },
        {
            "name": "Planet Dream",
            "type": "planet",
            "pos": [-25.0, -15.0, 10.0],
            "mass": 0.3,
            "color": "#00FFFF",
            "radius": 2.5
        }
    ]
    
    return {
        "attractors": attractors,
        "nodes": nodes,
        "lagrange": {} # Optional
    }
