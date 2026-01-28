
import sys
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import PeftModel

# Configuration
MODEL_NAME = "LiquidAI/LFM2-700M"
ADAPTER_PATH = "exports/ada-chakra-v1-knot/final_adapter"
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

def load_model():
    print(f"📥 Loading {MODEL_NAME}...")
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME, trust_remote_code=True)
    model = AutoModelForCausalLM.from_pretrained(MODEL_NAME, trust_remote_code=True, torch_dtype=torch.float16).to(DEVICE)
    
    print(f"🧬 Mounting Adapter: {ADAPTER_PATH}...")
    model = PeftModel.from_pretrained(model, ADAPTER_PATH)
    return model, tokenizer

def chat(model, tokenizer, prompt):
    # Format as User/Assistant
    text = f"User: {prompt}\nAssistant:"
    inputs = tokenizer(text, return_tensors="pt").to(DEVICE)
    
    with torch.no_grad():
        outputs = model.generate(
            **inputs, 
            max_new_tokens=60, 
            temperature=0.7, 
            do_sample=True,
            pad_token_id=tokenizer.eos_token_id
        )
    
    response = tokenizer.decode(outputs[0], skip_special_tokens=True)
    # Extract only the assistant part
    if "Assistant:" in response:
        response = response.split("Assistant:")[1].strip()
    return response

def main():
    print("🌈 Starting Chakra Test Suite...")
    model, tokenizer = load_model()
    
    prompts = [
        ("🔴 ROOT", "System status check."),
        ("🟠 SACRAL", "Generate a random idea."),
        ("🟡 SOLAR", "Who are you?"),
        ("🟢 HEART", "I am feeling lonely."),
        ("🔵 THROAT", "Print true."),
        ("🟣 THIRD EYE", "What is the pattern?"),
        ("⚪ CROWN", "Return NULL.")
    ]
    
    for chakra, p in prompts:
        print(f"\n{chakra} Prompt: {p}")
        response = chat(model, tokenizer, p)
        print(f"   Response: {response}")
        
    print("\n✅ Test Complete.")

if __name__ == "__main__":
    main()
