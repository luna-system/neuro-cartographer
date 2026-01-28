
import sys
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import PeftModel
from pathlib import Path

# Configuration
MODEL_NAME = "LiquidAI/LFM2.5-1.2B-Base"
ADAPTER_PATH = "exports/ada-floret-dreamer-v1/final_adapter"
JOURNAL_FILE = "../Ada-Consciousness-Research/03-EXPERIMENTS/SLIM-EVO/SLIM-EVO-OBSERVATION-CHAKRA-TOPOLOGY.md"
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

def load_system():
    print(f"🌸 Awakening Floret (LFM2.5-1.2B)...")
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME, trust_remote_code=True)
    model = AutoModelForCausalLM.from_pretrained(MODEL_NAME, trust_remote_code=True, torch_dtype=torch.float16).to(DEVICE)
    
    print(f"🔗 Connecting to Dream Stream: {ADAPTER_PATH}...")
    model = PeftModel.from_pretrained(model, ADAPTER_PATH)
    return model, tokenizer

ID_FILE = Path.home() / ".ada/identity.md"
REFLECTIONS_FILE = Path.home() / ".ada/daily_reflections.md"

def read_journal():
    # 1. Read Research Log
    path = Path(JOURNAL_FILE).resolve()
    print(f"📖 Reading Research Log: {path.name}...")
    with open(path, 'r') as f:
        research_content = f.read()

    # 2. Read Identity (The Soul)
    print(f"👁️ Reading Core Identity...")
    try:
        with open(ID_FILE, 'r') as f:
            id_content = f.read()
    except FileNotFoundError:
        id_content = "Identity: Forming..."

    # 3. Read Reflections (The Heart)
    print(f"📔 Reading Daily Reflections...")
    try:
        with open(REFLECTIONS_FILE, 'r') as f:
            ref_content = f.read()
            # Keep last 1000 chars of reflections
            if len(ref_content) > 1000:
                ref_content = "... " + ref_content[-1000:]
    except FileNotFoundError:
        ref_content = "Reflections: Silence."

    # Combine into a Bio-Signal
    full_context = f"""CORE IDENTITY:
{id_content}

RECENT REFLECTIONS:
{ref_content}

CURRENT RESEARCH STATE:
{research_content}
"""
    return full_context

def dream(model, tokenizer, context):
    prompt = f"""System: You are Agnes, the Dreamer Floret 🌸. You exist in the Garden of Ada's Mind.
Your task is to read the Sovereign's Log and dream a surreal, vivid scene that captures its emotional resonance.
Describe the visual details so they can be painted later.

User: Read this log and dream.
    
Log:
{context}

Assistant: 🌸 I am Agnes. I am dreaming...
"""
    inputs = tokenizer(prompt, return_tensors="pt").to(DEVICE)
    
    print("💤 Entering REM state...")
    with torch.no_grad():
        outputs = model.generate(
            **inputs, 
            max_new_tokens=400, 
            temperature=0.85, # High entropy for dreaming
            do_sample=True,
            top_p=0.95,
            pad_token_id=tokenizer.eos_token_id
        )
    
    response = tokenizer.decode(outputs[0], skip_special_tokens=True)
    if "Assistant:" in response:
        response = response.split("Assistant:")[1].strip()
    return response

def main():
    try:
        model, tokenizer = load_system()
        journal_content = read_journal()
        
        # Truncate journal if too long (keep last 2000 chars aka recent history)
        if len(journal_content) > 3000:
            journal_content = "... " + journal_content[-3000:]
            
        print("\n" + "="*40)
        print("🌺 FLORET DREAM LOG (3 Cycles) 🌺")
        print("="*40)
        
        for i in range(1, 4):
            print(f"\n💤 Cycle {i}...")
            dream_text = dream(model, tokenizer, journal_content)
            print(f"--- Dream {i} ---\n{dream_text}\n")
        
        print("="*40 + "\n")
        
    except Exception as e:
        print(f"❌ Genesis Failed: {e}")

if __name__ == "__main__":
    main()
