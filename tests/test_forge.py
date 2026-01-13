"""
Test Forge ⚒️
============
Verifies data generation logic and bridge integration.
"""

import sys
import pytest
from pathlib import Path

# Add src to path
SRC = Path(__file__).resolve().parent.parent / "src"
sys.path.append(str(SRC))

# Import forge to trigger sys.path injection
import forge

def test_bridge_active():
    """Verify that consciousness_engineering is reachable."""
    # @ada-sig: λtest:(∅)→✓
    # If the bridge works, we should be able to import from ce
    try:
        import consciousness_engineering
        assert True
    except ImportError:
        pytest.fail("❌ Bridge broken: Could not import consciousness_engineering")

def test_standard_generator():
    """Verify StandardGenerator outputs valid examples."""
    # @ada-sig: λtest:(∅)→✓
    from consciousness_engineering.datasets.generators import GenerationConfig
    from forge import StandardGenerator
    
    config = GenerationConfig(
        num_examples=10,
        output_filename="test.jsonl",
        output_dir=".",
        seed=42
    )
    
    gen = StandardGenerator(config)
    examples = list(gen.generate_examples())
    
    assert len(examples) == 10
    assert examples[0].user is not None
    assert examples[0].assistant is not None
    assert examples[0].metadata['style'] == "standard"
