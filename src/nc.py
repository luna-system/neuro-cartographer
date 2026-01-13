#!/usr/bin/env python3
"""
Neuro-Cartographer CLI (nc) 🗺️
==============================
The Sovereign Command Line.

Usage:
  nc forge data ...
  nc forge train ...
  nc map ...
  nc serve my_map.json
"""

import sys
import os
import shutil
import subprocess
import argparse
from pathlib import Path

# Paths
NC_ROOT = Path(__file__).resolve().parent.parent # neuro-cartographer
SRC_DIR = NC_ROOT / "src"
WEB_DIR = NC_ROOT / "web"
PUBLIC_DATA_DIR = WEB_DIR / "public" / "data"

def run_forge(args):
    """Delegate to forge.py"""
    # @ada-sig: λrun_forge:(Args)→⚡term
    # @ada-flow: invoke(forge.py) 
    cmd = [sys.executable, str(SRC_DIR / "forge.py")] + args.rest
    subprocess.run(cmd)

def run_map(args):
    """Delegate to map.py"""
    # @ada-sig: λrun_map:(Args)→⚡term
    # @ada-flow: invoke(map.py)
    cmd = [sys.executable, str(SRC_DIR / "map.py")] + args.rest
    subprocess.run(cmd)

def run_serve(args):
    """Serve a map file."""
    # @ada-sig: λrun_serve:(Args)→⚡server
    # @ada-flow: ?(exists)→copy→launch_astro ↳ ⊘error
    
    map_file = Path(args.map_file)
    if not map_file.exists():
        print(f"❌ Map file not found: {map_file}")
        return

    # 1. Copy to public/data
    target_name = map_file.name
    target_path = PUBLIC_DATA_DIR / target_name
    
    print(f"📦 Staging map at {target_path}...")
    shutil.copy2(map_file, target_path)
    
    # 2. Construct URL
    url = f"http://localhost:3000/?data=/data/{target_name}"
    print(f"🚀 Launching Orrery at: {url}")
    
    # 3. Run Astro (in web dir)
    # We use npm run dev -- --open (if supported) or just npm run dev
    try:
        subprocess.run(["npm", "run", "dev"], cwd=WEB_DIR)
    except KeyboardInterrupt:
        print("\n🛑 Server stopped.")

def main():
    # @ada-sig: λmain:()→⚡
    # @ada-flow: parse→dispatch(forge|map|serve) ↳ help
    
    parser = argparse.ArgumentParser(description="Neuro-Cartographer 🗺️", add_help=False)
    subparsers = parser.add_subparsers(dest="command", help="Command")

    # Forge
    forge_parser = subparsers.add_parser("forge", help="Data generation and Training")
    forge_parser.add_argument("rest", nargs=argparse.REMAINDER)

    # Map
    map_parser = subparsers.add_parser("map", help="Scan and Map a model")
    map_parser.add_argument("rest", nargs=argparse.REMAINDER)

    # Serve
    serve_parser = subparsers.add_parser("serve", help="Visualize a map")
    serve_parser.add_argument("map_file", help="Path to json map file")

    # Parse only the first arg to dispatch
    if len(sys.argv) < 2:
        parser.print_help()
        return

    # Dispatch manually to avoid argparse eating sub-flags
    cmd = sys.argv[1]
    
    class Args: pass

    if cmd == "forge":
        # Pass everything after 'forge' to forge.py
        args = Args()
        args.rest = sys.argv[2:]
        run_forge(args)
        
    elif cmd == "map":
        args = Args()
        args.rest = sys.argv[2:]
        run_map(args)
        
    elif cmd == "serve":
        # Let argparse handle serve since it has a specific arg
        args = parser.parse_args()
        run_serve(args)
        
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
