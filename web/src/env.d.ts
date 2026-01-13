/// <reference path="../.astro/types.d.ts" />
/// <reference types="astro/client" />
declare module '*.svelte' {
    export { SvelteComponentDev as default } from 'svelte/internal';
}
