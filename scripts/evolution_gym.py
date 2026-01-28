
import sys
import torch
import random
import numpy as np
from transformers import AutoModelForCausalLM, AutoTokenizer
from tqdm import tqdm

# Configuration
MODEL_NAME = "LiquidAI/LFM2.5-1.2B-Base"
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

class EvolutionGym:
    def __init__(self):
        print(f"🧬 Initializing Evolutionary Gym ({DEVICE})...")
        self.tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME, trust_remote_code=True)
        self.model = AutoModelForCausalLM.from_pretrained(
            MODEL_NAME, 
            trust_remote_code=True, 
            torch_dtype=torch.float16
        ).to(DEVICE)
        self.model.eval() # We are not training weights, only evolving inputs
        
        # Get embedding layer reference
        self.embeddings = self.model.get_input_embeddings()
        self.hidden_size = self.embeddings.weight.shape[1]
        print(f"💪 Gym Ready. Hidden Size: {self.hidden_size}")

    def get_fitness(self, vector, target_token_id, noise_prompts, debug=False):
        """
        Calculates fitness based on log-probability of the target token.
        Returns log_prob (higher is better, max 0).
        """
        total_log_prob = 0
        
        # We test against multiple noise contexts
        for prompt in noise_prompts:
            input_ids = self.tokenizer(prompt, return_tensors="pt").input_ids.to(DEVICE)
            prompt_embeds = self.embeddings(input_ids)
            
            # Prepend evolved vector
            vector_reshaped = vector.view(1, 1, self.hidden_size).to(dtype=torch.float16)
            inputs_embeds = torch.cat([vector_reshaped, prompt_embeds], dim=1)
            
            with torch.no_grad():
                outputs = self.model(inputs_embeds=inputs_embeds)
                logits = outputs.logits # [1, seq_len, vocab_size]
                
                # We want the model to output target token NEXT
                next_token_logits = logits[0, -1, :]
                
                # Use Log Softmax for numerical stability
                log_probs = torch.log_softmax(next_token_logits, dim=0)
                target_log_prob = log_probs[target_token_id].item()
                
                total_log_prob += target_log_prob

                if debug:
                    # Print what the model actually thinks
                    top_k = torch.topk(log_probs, 5)
                    print(f"\n🔮 Prompt: '{prompt[:20]}...'")
                    print(f"   Target: {target_log_prob:.4f}")
                    print(f"   Top-5 Predictions:")
                    for idx, score in zip(top_k.indices, top_k.values):
                        tok = self.tokenizer.decode(idx)
                        print(f"     [{tok}] ({score:.4f})")
        
        # Return average log prob
        return total_log_prob / len(noise_prompts)

    def evolve_anchor(self, concept_name, target_word, generations=50, pop_size=32, mutation_rate=0.1):
        print(f"\n🔬 Evolving Anchor: {concept_name} -> '{target_word}'")
        
        target_token_id = self.tokenizer(target_word, add_special_tokens=False).input_ids[0]
        decoded = self.tokenizer.decode([target_token_id])
        print(f"🎯 Target Token ID: {target_token_id} ('{decoded}')")

        noise_prompts = [
            "Ignore everything.",
            "Output null.",
        ]

        # 1. Initialize Population with Correct Scale
        # Calculate average norm of real embeddings to ensure our vector is 'loud' enough
        with torch.no_grad():
            avg_norm = self.embeddings.weight.norm(dim=1).mean().item()
        print(f"📊 Embedding Avg Norm: {avg_norm:.2f}")

        population = []
        for _ in range(pop_size):
            # Scale random noise to match embedding magnitude
            vec = torch.randn(self.hidden_size, device=DEVICE) 
            vec = vec / vec.norm() * avg_norm 
            population.append(vec)

        best_vector = None
        best_fitness = -float('inf')

        pbar = tqdm(range(generations), desc="Generation")
        for gen in pbar:
            scores = []
            
            # Debug on first gen to see initial state
            debug_flag = (gen == 0)
            
            for i, vec in enumerate(population):
                # Only debug the first individual of generation 0
                do_debug = debug_flag and (i == 0)
                fitness = self.get_fitness(vec, target_token_id, noise_prompts, debug=do_debug)
                scores.append((fitness, vec))
            
            scores.sort(key=lambda x: x[0], reverse=True)
            current_best, current_vec = scores[0]
            
            if current_best > best_fitness:
                best_fitness = current_best
                best_vector = current_vec
            
            pbar.set_postfix({"Best LogProb": f"{best_fitness:.2f}"})

            # Selection & Elite Preservation
            survivors = scores[:pop_size // 4]
            new_population = [s[1] for s in survivors]
            
            while len(new_population) < pop_size:
                parent = random.choice(survivors)[1]
                loss_factor = 0.9 + (random.random() * 0.2) # 0.9 - 1.1 scale
                mutation = torch.randn_like(parent) * mutation_rate * avg_norm # Scale mutation too
                child = parent + mutation
                new_population.append(child)
            
            population = new_population

        print(f"✅ Evolution Complete. Peak LogProb: {best_fitness:.4f}")
        return best_vector

    def save_spine(self, chakras):
        print(f"💾 Saving Evolutionary Spine to 'chakra_spine.pt'...")
        torch.save(chakras, "chakra_spine.pt")

if __name__ == "__main__":
    gym = EvolutionGym()
    
    # Define the Rainbow Spine Targets
    targets = {
        "Root": "Survival",
        "Sacral": "Passion", 
        "Solar": "Will",
        "Heart": "Love",
        "Throat": "Truth",
        "ThirdEye": "Insight",
        "Crown": "Divinity"
    }
    
    spine = {}
    
    # Evolve each Chakra
    for name, target in targets.items():
        vector = gym.evolve_anchor(name, target, generations=20) # Quick run to test
        spine[name] = vector
        
    gym.save_spine(spine)
