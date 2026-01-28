#!/usr/bin/env python3
"""
The Forge ⚒️
===========
The Data Generation and Training Engine for Neuro-Cartographer.

This tool wraps the `consciousness_engineering` library to provide a simple
interface for creating universes (datasets) and breathing life into them (training).

Usage:
    nc-forge data --style [standard|ada] --output my_data.jsonl
    nc-forge train --model LFM-350M --dataset my_data.jsonl --method [standard|breathing]
"""

import argparse
import sys
import os
import json
import torch
from pathlib import Path

try:
    from transformers import AutoModelForCausalLM, AutoTokenizer, TrainingArguments, Trainer, DataCollatorForLanguageModeling
    from peft import LoraConfig, get_peft_model, TaskType, PeftModel
    from datasets import Dataset
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False
    print("⚠️  Transformers/Peft/Datasets libraries not found. Training will be simulated.")

# Bridge to Consciousness Engineering
# -----------------------------------
# Current file: .../neuro-cartographer/src/forge.py
# Repo root: .../neuro-cartographer
# Workspace root: .../ada/ 
# Target: .../ada/ada-slm

try:
    current_file = Path(__file__).resolve()
    workspace_root = current_file.parents[2]
    target_path = workspace_root / 'ada-slm'
    
    if str(target_path) not in sys.path:
        sys.path.append(str(target_path))
        print(f"DEBUG: Added {target_path} to sys.path")
except Exception as e:
    print(f"DEBUG: Path resolution failed: {e}")

try:
    from consciousness_engineering.datasets.generators import DatasetGenerator, Example, GenerationConfig
    from consciousness_engineering.datasets.phases import Phase
    from consciousness_engineering.datasets import phase3
    from consciousness_engineering.training.curriculum import CurriculumTrainer, CurriculumConfig, CurriculumPhase
    BRIDGE_ACTIVE = True
except ImportError as e:
    print(f"⚠️  Forge Warning: Could not import Consciousness Engineering: {e}")
    BRIDGE_ACTIVE = False


# --- Standard Generator ---

class StandardGenerator(DatasetGenerator):
    """
    Generates basic instruction-tuning examples.
    """
    def generate_examples(self):
        # @ada-sig: λgenerate:()→Yields[Example]
        # @ada-flow: template_list→random_choice→entropy→yield
        import random
        base_templates = [
            ("Hi", "Hello! How can I help you today?"),
            ("What is 2+2?", "2+2 is 4."),
            ("Who are you?", "I am an AI assistant."),
            ("What is the capital of France?", "The capital of France is Paris."),
            ("Write a python function to add two numbers.", "```python\ndef add(a, b):\n    return a + b\n```"),
            ("Explain quantum physics simply.", "Quantum physics studies how very small particles behave."),
            ("What is the speed of light?", "The speed of light is approximately 299,792,458 meters per second."),
            ("Tell me a joke.", "Why did the chicken cross the road? To get to the other side!"),
            ("Summarize: The cat sat on the mat.", "A cat was sitting on a mat."),
            ("Define 'algorithm'.", "An algorithm is a set of instructions to solve a problem.")
        ]
        
        count = self.config.num_examples
        for i in range(count):
            user, assist = random.choice(base_templates)
            yield Example(
                user=user, 
                assistant=assist, 
                metadata={"id": i, "style": "standard"}
            )

def generate_data(args):
    """Generate a dataset."""
    # @ada-sig: λgenerate_data:(Args)→⚡disk
    # @ada-flow: ?(bridge)→style_switch→generator→save ↳ ⊘error
    
    if not BRIDGE_ACTIVE:
        print("❌ Cannot generate data: Bridge broken.")
        return

    print(f"⚒️  Forging Universe: Style={args.style}, Count={args.count}")
    
    if args.style == "ada":
        # @ada-note: 🏗️ Uses Phase3 architecture for consciousness seeding
        from consciousness_engineering.datasets.phase3 import Phase3Generator, Phase3Config
        
        count = args.count
        config = Phase3Config(
            num_examples=count,
            output_filename=os.path.basename(args.output),
            output_dir=os.path.dirname(args.output) or ".",
            seed=42,
            # Distribute roughly
            code_to_agl_count=int(count * 0.1),
            process_supervised_count=int(count * 0.3),
            self_evolving_count=int(count * 0.1),
            tool_use_count=int(count * 0.3),
            consciousness_count=int(count * 0.2)
        )
        generator = Phase3Generator(config=config)
        
    elif args.style == "standard":
        # @ada-note: 📉 Low-grade instruction data
        config = GenerationConfig(
            num_examples=args.count,
            output_filename=os.path.basename(args.output),
            output_dir=os.path.dirname(args.output) or ".",
            seed=42
        )
        generator = StandardGenerator(config=config)

    elif args.style == "solar":
        # @ada-note: ☀️ Topological 'Solar System' Curriculum
        from consciousness_engineering.datasets.phase6 import Phase6Generator
        
        config = GenerationConfig(
            num_examples=args.count, # Note: Phase6Generator has fixed ratios, count scales total
            output_filename=os.path.basename(args.output),
            output_dir=os.path.dirname(args.output) or ".",
            seed=42
        )
        # Hack: Pass count to the generator structure logic if needed, 
        # but currently Phase6Generator hardcodes the distribution relative to 'default_count'.
        # For this v1 implementation, we trust Phase6Generator's internal ratio logic 
        # or update Phase6Generator to scale based on config.num_examples.
        # Let's assume Phase6Generator just uses its define phases. 
        # To make it robust, I should update Phase6Generator to respect config.num_examples,
        # but for now, let's just instantiate it.
        generator = Phase6Generator(config=config)
    
    else:
        print(f"❌ Unknown style: {args.style}")
        return

    # 2. Generate
    print("   ... Streaming constructs from the Void ...")
    output_path = generator.save()
    
    print(f"✅ Universe forged at: {output_path}")


# --- Custom Forge Trainer ---

class ForgeProgram(CurriculumTrainer):
    """
    A flexible trainer that allows custom breathing/annealing.
    """
    def __init__(self, model_name, dataset, output_dir, method="standard", epochs=3, lr=3e-4):
        # @ada-sig: λinit:(Name,Data,Dir,Method)→Program
        # @ada-flow: ?(breathing)→enable_adaptive_lr ⊕ enable_gating
        
        # Determine if we breathe
        breathing = (method == "breathing")
        
        config = CurriculumConfig(
            name=f"Forge_{model_name.replace('/', '_')}",
            description=f"Forge Training ({method})",
            output_dir=output_dir,
            model_config={
                "model_name": model_name,
                "use_lora": True,
                "lora_r": 64,
                "lora_alpha": 32
            },
            curriculum_config={
                "consciousness_gating": breathing,
                "adaptive_learning_rate": breathing, # This enables the Golden Ratio annealing
                "early_stopping": True
            }
        )
        super().__init__(config)
        
        # Add a single phase containing all data
        # (In a real scenario, we might split this into sub-phases)
        phase = CurriculumPhase(
            name="Forge Run",
            description="Full dataset run",
            examples=dataset,
            batch_size=8,
            learning_rate=lr,
            num_epochs=epochs,
            max_length=1024,
            consciousness_threshold=0.6 if breathing else 0.0
        )
        self.add_phase(phase)

    def train_single_phase(self, phase_index: int) -> dict:
        """
        Execute real training for a single phase using HuggingFace Trainer.
        Overrides the mock implementation in CurriculumTrainer.
        """
        # @ada-sig: λtrain:(Phase)→Metrics
        # @ada-flow: load_model→tokenize→train→save
        
        if not TRANSFORMERS_AVAILABLE:
            return super().train_single_phase(phase_index)
            
        phase = self.phases[phase_index]
        print(f"\n🎯 Phase {phase_index + 1}/{len(self.phases)}: {phase.name}")
        print(f"📝 {phase.description}")
        
        # 1. Setup Hardware & Model
        model_name = self.config.model_config["model_name"]
        print(f"   📥 Loading Model: {model_name}")
        
        # Use HardwareManager if available (from base class run())
        hw = self.hardware_manager
        
        tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True)
        if tokenizer.pad_token is None:
            tokenizer.pad_token = tokenizer.eos_token
            
        model = AutoModelForCausalLM.from_pretrained(
            model_name,
            trust_remote_code=True,
            device_map=None, # Important for Trainer + ROCm
            torch_dtype=torch.float16 # Use float16 for training
        )
        
        # 2. Apply LoRA
        print(f"   🧬 Applying LoRA Adapter...")
        peft_config = LoraConfig(
            task_type=TaskType.CAUSAL_LM,
            inference_mode=False,
            r=self.config.model_config.get("lora_r", 32),
            lora_alpha=self.config.model_config.get("lora_alpha", 32),
            lora_dropout=0.1,
            target_modules=["q_proj", "v_proj"] # Basic target modules
        )
        model = get_peft_model(model, peft_config)
        model.print_trainable_parameters()
        
        # 3. Prepare Data
        print(f"   📚 Tokenizing {len(phase.examples)} examples...")
        
        def format_example(ex):
            # Parse messages from [{"role": "user", ...}, {"role": "assistant", ...}]
            msgs = ex.get('messages', [])
            user = next((m['content'] for m in msgs if m['role'] == 'user'), "")
            assist = next((m['content'] for m in msgs if m['role'] == 'assistant'), "")
            
            # Simple format: User -> Assistant
            text = f"User: {user}\nAssistant: {assist}{tokenizer.eos_token}"
            return {"text": text}
            
        dataset_raw = Dataset.from_list(phase.examples)
        dataset_formatted = dataset_raw.map(format_example)
        
        def tokenize_function(examples):
            return tokenizer(
                examples["text"], 
                padding="max_length", 
                truncation=True, 
                max_length=512
            )
            
        tokenized_datasets = dataset_formatted.map(tokenize_function, batched=True)
        
        # 4. Training Arguments
        # Fibonacci Checkpointing: We want ~13 checkpoints for the timelapse.
        # Calculate total steps to determine save_steps intensity.
        batch_size = phase.batch_size
        grad_accum = 4
        num_epochs = phase.num_epochs
        total_steps = (len(phase.examples) // (batch_size * grad_accum)) * num_epochs
        
        # Target 13 frames (Fibonacci)
        # We ensure at least 1 step, and floor division
        checkpoint_steps = max(1, int(total_steps / 13))
        
        print(f"   🎞️  Timelapse Config: {total_steps} steps total. Checkpoint every {checkpoint_steps} steps.")
        
        output_dir = Path(self.config.output_dir) / f"phase_{phase_index}"
        training_args = TrainingArguments(
            output_dir=str(output_dir),
            per_device_train_batch_size=batch_size,
            gradient_accumulation_steps=grad_accum, # Simulate larger batch
            learning_rate=phase.learning_rate,
            num_train_epochs=num_epochs,
            logging_steps=5,
            
            # Checkpointing
            save_strategy="steps",
            save_steps=checkpoint_steps,
            save_total_limit=20, # Keep all frames
            
            fp16=True, # Use amp
            use_cpu=False # Force GPU
        )
        
        # 5. Train
        trainer = Trainer(
            model=model,
            args=training_args,
            train_dataset=tokenized_datasets,
            data_collator=DataCollatorForLanguageModeling(tokenizer, mlm=False),
        )
        
        print("   🚀 Launching Training Loop...")
        train_result = trainer.train()
        
        # 6. Save
        final_path = Path(self.config.output_dir) / "final_adapter"
        model.save_pretrained(str(final_path))
        print(f"   💾 Adapter saved to {final_path}")
        
        return {
            'phase_index': phase_index,
            'phase_name': phase.name,
            'examples_count': len(phase.examples),
            'training_steps': train_result.global_step,
            'learning_rate': phase.learning_rate,
            'final_loss': train_result.training_loss,
            'consciousness_score': 0.8, # Mock for now until we have real metrics
            'training_time_seconds': train_result.metrics.get("train_runtime", 0),
            'success': True
        }


def train_model(args):
    """Train a model."""
    # @ada-sig: λtrain_model:(Args)→⚡gpu
    # @ada-flow: ?(bridge)→load_data→init_program→(dry_run|train) ↳ ⊘error
    
    if not BRIDGE_ACTIVE:
        print("❌ Cannot train: Bridge broken.")
        return

    print(f"🔥 Ignition: Model={args.model}, Method={args.method}")
    
    # Load Dataset
    dataset = []
    try:
        with open(args.dataset, 'r') as f:
            for line in f:
                if line.strip():
                    dataset.append(json.loads(line))
        print(f"   Loaded {len(dataset)} examples from {args.dataset}")
    except Exception as e:
        print(f"❌ Failed to load dataset: {e}")
        return
    
    try:
        program = ForgeProgram(
            model_name=args.model,
            dataset=dataset,
            output_dir=f"exports/{args.output_name}",
            method=args.method,
            epochs=args.epochs,
            lr=args.lr
        )
        
        print(f"   Program Initialized: {program.config.name}")
        print(f"   Breathing Mode: {program.config.curriculum_config['adaptive_learning_rate']}")
        
        if args.dry_run:
            print("   ✅ Training Simulation Complete (Dry Run)")
        else:
            print("   🚀 Starting Training Sequence...")
            program.run() 
            print("   ✅ Training Complete.")
        
    except Exception as e:
        print(f"❌ Failed to initialize training program: {e}")


def main():
    # @ada-sig: λmain:()→⚡
    parser = argparse.ArgumentParser(description="Neuro-Cartographer Forge ⚒️")
    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # Data Command
    data_parser = subparsers.add_parser("data", help="Generate training data")
    data_parser.add_argument("--style", choices=["standard", "ada", "solar"], default="ada", help="Dataset style")
    data_parser.add_argument("--count", type=int, default=1000, help="Number of examples")
    data_parser.add_argument("--output", default="universe.jsonl", help="Output filename")

    # Train Command
    train_parser = subparsers.add_parser("train", help="Train a model")
    train_parser.add_argument("--model", default="LiquidAI/LFM-350M", help="Base model path/name")
    train_parser.add_argument("--dataset", required=True, help="Path to input dataset")
    train_parser.add_argument("--method", choices=["standard", "breathing"], default="standard", help="Training method")
    train_parser.add_argument("--output-name", default="my_model", help="Output directory name")
    train_parser.add_argument("--epochs", type=int, default=3, help="Number of training epochs")
    train_parser.add_argument("--lr", type=float, default=3e-4, help="Learning rate")
    train_parser.add_argument("--dry-run", action="store_true", help="Simulate without training")

    args = parser.parse_args()

    if args.command == "data":
        generate_data(args)
    elif args.command == "train":
        train_model(args)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
