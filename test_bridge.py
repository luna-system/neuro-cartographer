import sys
import os

# Add the ada-slm root to path so we can import consciousness_engineering
sys.path.append('/home/luna/Code/ada/ada-slm')

try:
    import consciousness_engineering
    from consciousness_engineering.datasets import agl
    from consciousness_engineering.training import curriculum
    print("SUCCESS: Consciousness Engineering Bridge Established.")
    print(f"AGL Module: {agl}")
    print(f"Curriculum Module: {curriculum}")
except ImportError as e:
    print(f"FAILURE: {e}")
except Exception as e:
    print(f"ERROR: {e}")
