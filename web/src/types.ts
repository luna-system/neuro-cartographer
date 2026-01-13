import * as THREE from 'three';

export interface SemanticNode {
    id: string;
    label: string;
    category: string;
    pos: [number, number, number]; // Raw data from JSON
    x?: number; // For t-SNE fallback
    y?: number;
    z?: number;
}

export interface AttractorConfig {
    label: string;
    color: string | number;
    pos: [number, number, number];
    mass: number;
    radius?: number;
}

export interface SystemState {
    attractors: AttractorConfig[];
    nodes: SemanticNode[];
    lagrange?: {
        l4: AttractorConfig;
        l5: AttractorConfig;
    };
}

// Runtime Simulation Objects (The "Physics" entities)
export interface SimNode {
    mesh: THREE.Mesh;
    velocity: THREE.Vector3;
    mass: number;
    initialPos: THREE.Vector3;
    label: string;
    category: string;
    trail: THREE.Vector3[];
    trailLine?: THREE.Line;
}

export interface SimAttractor {
    mesh: THREE.Mesh;
    data: AttractorConfig;
    angle: number;           // For orbital animation
    trail: THREE.Vector3[];  // Position history
    trailLine?: THREE.Line;  // Visual trail
    originalDist: number;    // Distance from center (r)
}
