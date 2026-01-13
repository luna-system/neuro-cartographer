<script lang="ts">
  import { createEventDispatcher } from 'svelte';
  import type { SimNode } from '../types';
  
  export let isSimulating = false;
  export let showTrails = false;
  export let selectedNode: SimNode | null = null;
  
  const dispatch = createEventDispatcher();

  function handleFileSelect(event: Event) {
      const input = event.target as HTMLInputElement;
      if (!input.files?.length) return;
      const file = input.files[0];
      const reader = new FileReader();
      reader.onload = (e) => {
          if (e.target?.result) {
              try {
                  const data = JSON.parse(e.target.result as string);
                  dispatch('loadData', data);
              } catch (err) {
                  alert('Invalid JSON map file');
              }
          }
      };
      reader.readAsText(file);
  }
</script>

<div class="hud">
    <div class="header">
        <h1>Neuro Cartographer</h1>
        <div class="status">v1.0</div>
    </div>

    <!-- Controls -->
    <div class="panel">
        <label class="file-btn">
            📂 Load Map
            <input type="file" accept=".json" on:change={handleFileSelect}>
        </label>

        <div class="divider"></div>

        <button class:active={isSimulating} on:click={() => dispatch('toggle')}>
            {isSimulating ? '⏸ Pause' : '▶ Simulate'}
        </button>
        <button on:click={() => dispatch('reset')}>↺ Reset</button>
        
        <button class:active={showTrails} on:click={() => dispatch('toggleTrails')}>
            {showTrails ? '〰 Trails: ON' : '〰 Trails: OFF'}
        </button>
    </div>

    <div class="meta">
        Drag to Orbit • Scroll to Zoom • Click to Inspect
    </div>

    <!-- Inspector -->
    {#if selectedNode}
        <div class="inspector">
            <h3>{selectedNode.label}</h3>
            <div class="type">{selectedNode.category}</div>
            <div class="coords">
                [{selectedNode.mesh.position.x.toFixed(2)}, 
                 {selectedNode.mesh.position.y.toFixed(2)}, 
                 {selectedNode.mesh.position.z.toFixed(2)}]
            </div>
            
            <!-- Metadata Render (AGL support) -->
            {#if selectedNode.metadata && Object.keys(selectedNode.metadata).length > 0}
                <div class="details">
                   {#each Object.entries(selectedNode.metadata) as [k, v]}
                        {#if k !== 'label' && k !== 'category' && k !== 'pos'}
                            <div class="kv">
                                <span class="key">{k}:</span> 
                                <span class="val">{v}</span>
                            </div>
                        {/if}
                   {/each}
                </div>
            {/if}
        </div>
    {/if}
</div>

<style>
    .hud {
        position: absolute;
        top: 20px;
        left: 20px;
        z-index: 10;
        pointer-events: none;
        display: flex;
        flex-direction: column;
        gap: 10px;
        max-width: 300px;
    }
    
    .header {
        display: flex;
        align-items: baseline;
        gap: 10px;
    }

    .status {
        font-family: monospace;
        color: #666;
        font-size: 0.8rem;
    }
    
    h1 {
        margin: 0;
        font-family: 'Inter', sans-serif;
        font-size: 1.2rem;
        background: linear-gradient(90deg, #00ffff, #ff00ff);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-transform: uppercase;
        letter-spacing: 2px;
    }

    .panel {
        pointer-events: auto;
        display: flex;
        flex-wrap: wrap;
        gap: 8px;
        background: rgba(10, 10, 15, 0.8);
        padding: 10px;
        border: 1px solid #333;
        border-radius: 6px;
        backdrop-filter: blur(8px);
    }
    
    .divider {
        width: 1px;
        background: #444;
        margin: 0 4px;
    }

    input[type="file"] {
        display: none;
    }

    .file-btn {
        background: #222;
        border: 1px solid #555;
        color: #ccc;
        padding: 6px 12px;
        border-radius: 4px;
        cursor: pointer;
        font-family: monospace;
        font-size: 0.8rem;
        transition: all 0.2s;
    }
    .file-btn:hover { border-color: #fff; color: #fff; }

    button {
        background: #222;
        border: 1px solid #444;
        color: #eee;
        padding: 6px 12px;
        border-radius: 4px;
        cursor: pointer;
        font-family: monospace;
        font-size: 0.8rem;
        transition: all 0.2s;
    }

    button:hover {
        border-color: #00ffff;
        background: rgba(40, 40, 60, 0.9);
    }

    button.active {
        background: rgba(0, 255, 255, 0.1);
        border-color: #00ffff;
        color: #00ffff;
    }

    .meta {
        font-family: monospace;
        font-size: 0.7rem;
        color: #666;
    }

    .inspector {
        pointer-events: auto;
        background: rgba(10, 10, 15, 0.9);
        border: 1px solid #00ffff;
        padding: 15px;
        border-radius: 6px;
        margin-top: 10px;
        box-shadow: 0 0 10px rgba(0, 255, 255, 0.1);
    }

    .inspector h3 {
        margin: 0 0 5px 0;
        color: #fff;
        font-family: 'Inter', sans-serif;
        font-size: 1rem;
    }

    .type {
        color: #ff00ff;
        font-size: 0.8rem;
        text-transform: uppercase;
        margin-bottom: 5px;
        font-family: monospace;
    }

    .coords {
        font-family: monospace;
        color: #666;
        font-size: 0.7rem;
        margin-bottom: 10px;
    }
    
    .details {
        display: flex;
        flex-direction: column;
        gap: 4px;
        font-size: 0.8rem;
        border-top: 1px solid #333;
        padding-top: 5px;
        max-height: 200px;
        overflow-y: auto;
    }
    
    .kv { color: #aaa; font-family: monospace; }
    .key { color: #888; }
    .val { color: #ddd; white-space: pre-wrap; }
</style>
