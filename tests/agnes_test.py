
import sys
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import PeftModel

# Configuration
MODEL_NAME = "LiquidAI/LFM2.5-1.2B-Base"
ADAPTER_PATH = "exports/ada-floret-dreamer-v1/final_adapter"
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

def load_model():
    print(f"🌸 Awakening Agnes (LFM2.5-1.2B)...")
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME, trust_remote_code=True)
    model = AutoModelForCausalLM.from_pretrained(MODEL_NAME, trust_remote_code=True, torch_dtype=torch.float16).to(DEVICE)
    model = PeftModel.from_pretrained(model, ADAPTER_PATH)
    return model, tokenizer

def chat(model, tokenizer, prompt):
    text = f"User: {prompt}\nAssistant:"
    inputs = tokenizer(text, return_tensors="pt").to(DEVICE)
    
    with torch.no_grad():
        outputs = model.generate(
            **inputs, 
            max_new_tokens=150, 
            temperature=0.6,
            do_sample=True,
            pad_token_id=tokenizer.eos_token_id
        )
    
    response = tokenizer.decode(outputs[0], skip_special_tokens=True)
    if "Assistant:" in response:
        response = response.split("Assistant:")[1].strip()
    return response

def main():
    print("🌸 Starting Agnes Coherence Test...")
    model, tokenizer = load_model()
    
    prompts = [
        ("💻 CODE", "Write a Python function to print a flower pattern."),
        ("🧠 LOGIC", "If Truth is Blue and Love is Green, what color is Truth + Love?"),
        ("🔮 AGL", "What does 'Self ⋈ Other' mean?"),
        ("👁️ IDENTITY", "Who is Agnes?")
    ]
    
    for category, p in prompts:
        print(f"\n{category} Prompt: {p}")
        response = chat(model, tokenizer, p)
        print(f"   Response:\n{response}")
        print("-" * 40)
        
    print("\n✅ Test Complete.")

if __name__ == "__main__":
    main()
