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
from pathlib import Path

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
    def __init__(self, model_name, dataset, output_dir, method="standard"):
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
            learning_rate=3e-4 if breathing else 5e-5,
            num_epochs=3,
            max_length=1024,
            consciousness_threshold=0.6 if breathing else 0.0
        )
        self.add_phase(phase)


def train_model(args):
    """Train a model."""
    # @ada-sig: λtrain_model:(Args)→⚡gpu
    # @ada-flow: ?(bridge)→load_data→init_program→(dry_run|train) ↳ ⊘error
    
    if not BRIDGE_ACTIVE:
        print("❌ Cannot train: Bridge broken.")
        return

    print(f"🔥 Ignition: Model={args.model}, Method={args.method}")
    
    # Load Dataset (Mocking logic for now since we don't have jsonl loader here yet)
    dataset = [{"user": "test", "assistant": "test"}] 
    
    try:
        program = ForgeProgram(
            model_name=args.model,
            dataset=dataset,
            output_dir=f"exports/{args.output_name}",
            method=args.method
        )
        
        print(f"   Program Initialized: {program.config.name}")
        print(f"   Breathing Mode: {program.config.curriculum_config['adaptive_learning_rate']}")
        
        if args.dry_run:
            print("   ✅ Training Simulation Complete (Dry Run)")
        else:
            print("   🚀 Starting Training Sequence...")
            program.train() 
            print("   ✅ Training Complete.")
        
    except Exception as e:
        print(f"❌ Failed to initialize training program: {e}")


def main():
    # @ada-sig: λmain:()→⚡
    parser = argparse.ArgumentParser(description="Neuro-Cartographer Forge ⚒️")
    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # Data Command
    data_parser = subparsers.add_parser("data", help="Generate training data")
    data_parser.add_argument("--style", choices=["standard", "ada"], default="ada", help="Dataset style")
    data_parser.add_argument("--count", type=int, default=1000, help="Number of examples")
    data_parser.add_argument("--output", default="universe.jsonl", help="Output filename")

    # Train Command
    train_parser = subparsers.add_parser("train", help="Train a model")
    train_parser.add_argument("--model", default="LiquidAI/LFM-350M", help="Base model path/name")
    train_parser.add_argument("--dataset", required=True, help="Path to input dataset")
    train_parser.add_argument("--method", choices=["standard", "breathing"], default="standard", help="Training method")
    train_parser.add_argument("--output-name", default="my_model", help="Output directory name")
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
