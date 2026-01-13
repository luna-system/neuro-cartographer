<script lang="ts">
  import { onMount, onDestroy } from 'svelte';
  import * as THREE from 'three';
  import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
  import { CSS2DRenderer, CSS2DObject } from 'three/addons/renderers/CSS2DRenderer.js';
  import type { SystemState, SimNode, SimAttractor } from '../types';
  import Hud from './Hud.svelte';

  // Props
  export let dataUrl: string = ''; // Default empty (Void State)
  
  // Check URL params for data override
  if (typeof window !== 'undefined') {
      const params = new URLSearchParams(window.location.search);
      const urlParam = params.get('data');
      if (urlParam) dataUrl = urlParam;
  }
  
  // State
  let container: HTMLDivElement;
  let loading = false;
  let error: string | null = null;
  
  // Simulation Flags
  let isSimulating = false;
  let showTrails = false;
  let selectedNode: SimNode | null = null; // Passed to HUD

  // Three.js Globals
  let scene: THREE.Scene;
  let camera: THREE.PerspectiveCamera;
  let renderer: THREE.WebGLRenderer;
  let labelRenderer: CSS2DRenderer;
  let controls: OrbitControls;
  let animationId: number;
  let raycaster: THREE.Raycaster;
  let mouse: THREE.Vector2;

  // Simulation Entities
  let nodes: SimNode[] = [];
  let attractors: SimAttractor[] = [];

  // Physics Config
  const G_CONST = 0.5;
  const DRAG = 0.98;
  const TRAIL_LENGTH = 50; 

  // Colors
  const CAT_COLORS: { [key: string]: number } = {
    "agl_awareness": 0xFFFF00,
    "logic": 0xFFA500,
    "emotion": 0x90EE90,
    "philosophy": 0x9370DB,
    "coding": 0x00BFFF,
    "default": 0xFFFFFF
  };

  function getColor(cat: string): number {
    for (const key in CAT_COLORS) {
      if (cat.includes(key) || key === cat) return CAT_COLORS[key];
    }
    return 0xAAAAAA;
  }

  // --- Initialization ---
  onMount(async () => {
    try {
      if (!container) return;
      initScene();
      
      // Only load if explicit URL provided
      if (dataUrl) {
          loading = true;
          await loadData(dataUrl);
      }
      
      animate();
      window.addEventListener('resize', onResize);
      window.addEventListener('mousemove', onMouseMove);
      window.addEventListener('click', onClick); // For selection
    } catch (e: any) {
      error = e.message;
      loading = false;
    }
  });

  onDestroy(() => {
    if (typeof window !== 'undefined') {
      cancelAnimationFrame(animationId);
      window.removeEventListener('resize', onResize);
      window.removeEventListener('mousemove', onMouseMove);
      window.removeEventListener('click', onClick);
      renderer?.dispose();
    }
  });

  function initScene() {
    scene = new THREE.Scene();
    scene.background = new THREE.Color(0x050508);

    camera = new THREE.PerspectiveCamera(60, window.innerWidth / window.innerHeight, 0.1, 1000);
    camera.position.set(0, 30, 40);

    renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
    renderer.setSize(window.innerWidth, window.innerHeight);
    renderer.setPixelRatio(window.devicePixelRatio);
    container.appendChild(renderer.domElement);

    labelRenderer = new CSS2DRenderer();
    labelRenderer.setSize(window.innerWidth, window.innerHeight);
    labelRenderer.domElement.style.position = 'absolute';
    labelRenderer.domElement.style.top = '0px';
    labelRenderer.domElement.style.pointerEvents = 'none';
    container.appendChild(labelRenderer.domElement);

    controls = new OrbitControls(camera, renderer.domElement);
    controls.enableDamping = true;
    controls.dampingFactor = 0.05;

    // Lights
    scene.add(new THREE.AmbientLight(0x404040));
    scene.add(new THREE.PointLight(0xffffff, 2, 100));

    // Helpers
    scene.add(new THREE.GridHelper(50, 50, 0x222222, 0x111111));

    raycaster = new THREE.Raycaster();
    mouse = new THREE.Vector2();
  }

  async function loadData(url: string) {
    const res = await fetch(url);
    if (!res.ok) throw new Error("Failed to fetch data");
    const data: SystemState = await res.json();
    buildSystem(data);
    loading = false;
  }
  
  function handleLoadData(event: CustomEvent) {
      // Clear existing
      clearSystem();
      buildSystem(event.detail);
  }

  function clearSystem() {
      // Remove existing meshes
      nodes.forEach(n => {
          scene.remove(n.mesh); 
          if(n.trailLine) scene.remove(n.trailLine);
      });
      attractors.forEach(a => {
           scene.remove(a.mesh);
           if(a.trailLine) scene.remove(a.trailLine);
           // Remove CSS label (child of mesh usually, but we attached strictly)
           // Actually CSS object logic: we added it to sphere, removing sphere removes it from layout? 
           // Need to ensure cleanup.
      });
      
      // Also remove CSS labels explicitly if needed, but ThreeJS handles children
      nodes = [];
      attractors = [];
      selectedNode = null;
  }

  function buildSystem(data: SystemState) {
    // 1. Attractors
    data.attractors.forEach(attr => {
      const geometry = new THREE.SphereGeometry(attr.radius || 1, 32, 32);
      const material = new THREE.MeshBasicMaterial({
        color: attr.color,
        wireframe: true,
        transparent: true,
        opacity: 0.8
      });
      const sphere = new THREE.Mesh(geometry, material);
      sphere.position.set(...attr.pos);
      
      // Metadata
      sphere.userData = { 
        label: attr.label, 
        mass: attr.mass,
        isAttractor: true 
      };

      scene.add(sphere);

      // Create Sim Object
      const simAttr: SimAttractor = {
        mesh: sphere,
        data: attr,
        angle: 0,
        trail: [],
        originalDist: sphere.position.length()
      };

      // Trail Line
      const trailGeo = new THREE.BufferGeometry();
      const trailMat = new THREE.LineBasicMaterial({ 
          color: attr.color, 
          transparent: true, 
          opacity: 0.3 
      });
      simAttr.trailLine = new THREE.Line(trailGeo, trailMat);
      // Only visible if flag, but we add to scene and toggle visibility in loop
      scene.add(simAttr.trailLine);

      // Label (CSS2D)
      const div = document.createElement('div');
      div.className = 'label';
      div.textContent = attr.label;
      const label = new CSS2DObject(div);
      label.position.set(0, (attr.radius||1) * 2.5, 0);
      div.style.color = typeof attr.color === 'string' ? attr.color : '#' + attr.color.toString(16);
      sphere.add(label);

      attractors.push(simAttr);
    });

    // 2. Nodes
    const nodeGeo = new THREE.SphereGeometry(0.3, 8, 8);
    data.nodes.forEach(n => {
      const color = getColor(n.category);
      const mat = new THREE.MeshBasicMaterial({ color });
      const mesh = new THREE.Mesh(nodeGeo, mat);
      
      const pos = n.pos ? n.pos : [n.x||0, n.y||0, n.z||0];
      mesh.position.set(pos[0], pos[1], pos[2]);
      
      mesh.userData = { 
        id: n.id,
        label: n.label, 
        category: n.category,
        metadata: n.metadata 
      };

      scene.add(mesh);
      
      // Node Trail
      const trailGeo = new THREE.BufferGeometry();
      const trailMat = new THREE.LineBasicMaterial({
          color: color,
          transparent: true,
          opacity: 0.2
      });
      const trailLine = new THREE.Line(trailGeo, trailMat);
      scene.add(trailLine);

      nodes.push({
        mesh,
        velocity: new THREE.Vector3(0, 0, 0),
        mass: 1.0,
        initialPos: new THREE.Vector3(pos[0], pos[1], pos[2]),
        label: n.label,
        category: n.category,
        trail: [],
        trailLine,
        metadata: n.metadata 
      });
    });
  }

  // --- Physics Loop ---
  function physicsStep() {
    const tempVec = new THREE.Vector3();

    nodes.forEach(node => {
      const force = new THREE.Vector3(0, 0, 0);

      attractors.forEach(att => {
        tempVec.subVectors(att.mesh.position, node.mesh.position);
        
        const distSq = tempVec.lengthSq(); 
        const dist = Math.sqrt(distSq);

        if (dist > 0.5) { 
           // F = G * M / r^2
           const strength = (G_CONST * att.data.mass) / (distSq + 0.1);
           tempVec.normalize().multiplyScalar(strength);
           force.add(tempVec);
        }
      });

      node.velocity.add(force);
      node.velocity.multiplyScalar(DRAG);
      node.mesh.position.add(node.velocity);
    });
  }

  function animate() {
    animationId = requestAnimationFrame(animate);
    controls.update();

    // Toggle Trail Visibility
    // Optimization: Only update visible property if changed? 
    // For now, just setting it every frame is cheap enough for JS prop
    nodes.forEach(n => { if (n.trailLine) n.trailLine.visible = showTrails; });
    attractors.forEach(a => { if (a.trailLine) a.trailLine.visible = showTrails; });

    if (isSimulating) {
      // 1. Attractors (Static Trails)
       attractors.forEach(att => {
         if (showTrails) {
             att.trail.push(att.mesh.position.clone());
             if (att.trail.length > TRAIL_LENGTH) att.trail.shift();
             if (att.trailLine) att.trailLine.geometry.setFromPoints(att.trail);
         }
       });

      // 2. Move Nodes
      physicsStep();
      
      nodes.forEach(n => {
          if (showTrails) {
              n.trail.push(n.mesh.position.clone());
              if (n.trail.length > TRAIL_LENGTH) n.trail.shift();
              if (n.trailLine) n.trailLine.geometry.setFromPoints(n.trail);
          }
      });
    }

    renderer.render(scene, camera);
    labelRenderer.render(scene, camera);
  }

  // --- Events ---
  function onResize() {
    camera.aspect = window.innerWidth / window.innerHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(window.innerWidth, window.innerHeight);
    labelRenderer.setSize(window.innerWidth, window.innerHeight);
  }

  function onMouseMove(event: MouseEvent) {
    mouse.x = (event.clientX / window.innerWidth) * 2 - 1;
    mouse.y = -(event.clientY / window.innerHeight) * 2 + 1;
  }
  
  function onClick(event: MouseEvent) {
      if (!raycaster) return;
      
      // Raycast against nodes
      raycaster.setFromCamera(mouse, camera);
      const meshes = nodes.map(n => n.mesh);
      const intersects = raycaster.intersectObjects(meshes);
      
      if (intersects.length > 0) {
          // Found a node
          const mesh = intersects[0].object;
          // Find SimNode (using userData or reference)
          // userData has keys, but we need the full SimNode for inspector if props differ
          // We can find by mesh reference
          selectedNode = nodes.find(n => n.mesh === mesh) || null;
      } else {
          // Deselect if clicked background (unless dragging?)
          // Check if dragging logic handled by controls?
          // For now, simple click-away to deselect
          selectedNode = null;
      }
  }

  function resetSimulation() {
    isSimulating = false;
    nodes.forEach(n => {
        n.mesh.position.copy(n.initialPos);
        n.velocity.set(0, 0, 0);
        n.trail = [];
        if (n.trailLine) n.trailLine.geometry.setFromPoints([]);
    });
    attractors.forEach(a => {
        a.mesh.position.set(...a.data.pos); 
        a.angle = 0;
        a.trail = [];
        if (a.trailLine) a.trailLine.geometry.setFromPoints([]);
    });
  }
</script>

<div class="orrery-container" bind:this={container}>
    <Hud 
        {isSimulating}
        {showTrails}
        {selectedNode}
        
        on:toggle={() => isSimulating = !isSimulating}
        on:reset={resetSimulation}
        on:toggleTrails={() => showTrails = !showTrails}
        on:loadData={handleLoadData}
    />

    {#if loading}
        <div class="loading">Parsing Neural Maps...</div>
    {/if}
    
    {#if nodes.length === 0 && !loading && !error}
         <div class="empty-state">
             <div class="void-msg">🌌 The Void Awaits</div>
             <div class="sub-msg">Load a Map to Begin</div>
         </div>
    {/if}

    {#if error}
        <div class="error">{error}</div>
    {/if}
</div>

<style>
    .orrery-container {
        width: 100vw;
        height: 100vh;
        overflow: hidden;
        background: black;
        position: relative;
    }
    .loading, .error, .empty-state {
        position: absolute;
        top: 50%; 
        left: 50%;
        transform: translate(-50%, -50%);
        color: #00ffff;
        font-family: monospace;
        text-align: center;
        pointer-events: none;
    }
    .error { color: #ff0055; }
    
    .void-msg {
        font-size: 2rem;
        letter-spacing: 5px;
        color: #333;
        text-transform: uppercase;
        animation: pulse 4s infinite;
    }
    .sub-msg { color: #555; }
    
    @keyframes pulse {
        0% { opacity: 0.5; }
        50% { opacity: 1; text-shadow: 0 0 10px #00ffff; }
        100% { opacity: 0.5; }
    }
    
    :global(.label) {
        font-family: 'Inter', sans-serif;
        font-size: 12px;
        text-shadow: 0 0 4px black;
        pointer-events: none;
    }
</style>
