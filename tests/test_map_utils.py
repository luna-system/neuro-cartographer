"""
Test Map Utils 🗺️
================
Verifies IO and prompt loading logic.
"""

import sys
import json
import pytest
from pathlib import Path

# Add src to path
SRC = Path(__file__).resolve().parent.parent / "src"
sys.path.append(str(SRC))

from map import load_prompts

def test_load_jsonl(tmp_path):
    """Verify loading from JSONL."""
    # @ada-sig: λtest:(tmp)→✓
    
    # Create dummy file
    f = tmp_path / "test.jsonl"
    with open(f, "w") as fp:
        fp.write('{"user": "q1", "assistant": "a1"}\n')
        fp.write('{"label": "direct_label", "category": "cat"}\n')
        
    items = load_prompts(str(f))
    
    # We logic'd that "assistant" becomes the label if "label" missing
    assert len(items) == 2
    assert items[0]["label"] == "a1" # from assistant
    assert items[1]["label"] == "direct_label" # explicit

def test_load_txt(tmp_path):
    """Verify loading from TXT."""
    # @ada-sig: λtest:(tmp)→✓
    f = tmp_path / "test.txt"
    with open(f, "w") as fp:
        fp.write("Hello World\n")
        fp.write("Analysis complete\n")
        
    items = load_prompts(str(f))
    
    assert len(items) == 2
    assert items[0]["label"] == "Hello World"
    assert items[0]["category"] == "text"

def test_load_system_state(tmp_path):
    """Verify loading from existing system_state.json."""
    # @ada-sig: λtest:(tmp)→✓
    f = tmp_path / "map.json"
    data = {
        "nodes": [
            {"id": 1, "label": "Node1", "pos": [0,0,0]}
        ]
    }
    with open(f, "w") as fp:
        json.dump(data, fp)
        
    items = load_prompts(str(f))
    
    assert len(items) == 1
    assert items[0]["label"] == "Node1"
