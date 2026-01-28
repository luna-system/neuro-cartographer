
from transformers import AutoConfig, AutoModelForCausalLM, AutoTokenizer
import sys

model_id = "LiquidAI/LFM2-8B-A1B"

print("Loading Config...")
try:
    config = AutoConfig.from_pretrained(model_id, trust_remote_code=True)
    print("✅ Config Loaded")
    print(config)
except Exception as e:
    print(f"❌ Config Failed: {e}")

print("\nLoading Tokenizer...")
try:
    # Adding trust_remote_code
    tokenizer = AutoTokenizer.from_pretrained(model_id, trust_remote_code=True)
    print("✅ Tokenizer Loaded")
except Exception as e:
    print(f"❌ Tokenizer Failed: {e}")
    
# Not loading model to save time/bandwidth/VRAM
