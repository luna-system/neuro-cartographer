"""
Test Projector 📽️
=================
Verifies the dimensionality reduction logic.
"""

import sys
import numpy as np
import pytest
from pathlib import Path

# Add src to path
SRC = Path(__file__).resolve().parent.parent / "src"
sys.path.append(str(SRC))

from projector import Projector, build_system_state

def test_projector_shape():
    """Verify output shape is (N, 3)."""
    # @ada-sig: λtest:(∅)→✓
    # Generate 10 random vectors of dim 768
    N = 10
    dim = 768
    vectors = np.random.rand(N, dim)
    
    projector = Projector(method="pca") # PCA is deterministic & fast for tests
    coords = projector.project(vectors)
    
    assert coords.shape == (N, 3)
    assert isinstance(coords, np.ndarray)

def test_projector_scaling():
    """Verify coordinates are normalized roughly to [-60, 60]."""
    # @ada-sig: λtest:(∅)→✓
    vectors = np.random.rand(50, 64)
    projector = Projector(method="pca")
    coords = projector.project(vectors)
    
    max_val = np.max(np.abs(coords))
    assert max_val <= 60.01 # Allow floating point margin
    # Should be exactly 60 unless all zeros
    if np.any(vectors):
         assert np.isclose(max_val, 60.0)

def test_build_system_state():
    """Verify JSON structure creation."""
    # @ada-sig: λtest:(∅)→✓
    coords = np.array([
        [10.0, 0.0, 0.0],
        [0.0, 20.0, 0.0],
        [0.0, 0.0, 30.0]
    ])
    metadata = [
        {"label": "A", "category": "cat1"},
        {"label": "B", "category": "cat2"},
        {"label": "C", "category": "cat3"}
    ]
    
    state = build_system_state(coords, metadata)
    
    assert "nodes" in state
    assert len(state["nodes"]) == 3
    assert state["nodes"][0]["pos"] == [10.0, 0.0, 0.0]
    assert state["nodes"][1]["label"] == "B"
    assert "attractors" in state
    assert len(state["attractors"]) >= 1
