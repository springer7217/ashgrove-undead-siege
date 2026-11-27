# Ashgrove: Undead Siege

A dense single-file browser multiplayer zombie survival FPS built with AI assistance (Claude) by a high school developer with no prior technical background.

## Overview
- Full WebGL rendering (Three.js-style with SMAA/FXAA post-processing)
- Extensive custom weapon systems with unique per-kill VFX (dozens of themed effects)
- Bots with imperfect aim, reactions, and progression
- Team modes, multiplayer elements, arenas/maps
- Polished HUD, menus, settings, and Pixel Gun 3D-inspired UI elements

## Important Notice (Anti-Cheat)
The original file starts with a strong notice warning against adding cheats, aimbots, wallhacks, god mode, patchers, or anything that disables anti-cheat, version checks, or bank code. A previous player used AI assistants to create unauthorized "dev build" tools by claiming to be the developer. Ordinary improvements (bug fixes, accessibility, explanations) are welcome. Cheat tools are not.

Respect the original author's intent.

## Running Locally
1. Clone this repository
2. Place the full original `index.html` (from the Google Drive source) in the root of the repo
3. Open `index.html` in a modern browser
4. No build step required — it is a pure static single-file game

## Deployment
This repository is set up for Vercel static hosting. Once the full `index.html` is committed and the project is linked to Vercel, pushes to `main` will deploy automatically.

## Future Improvements
- Extract CSS into a separate `styles.css`
- Modularize JavaScript (weapons, renderer, bots, multiplayer, VFX)
- Extract base64-encoded assets into proper image/model files
- Add a lightweight build process if modularization proceeds

## Credits
Original creation: High school developer using Claude / AI assistance.
Repository structured and prepared for GitHub + Vercel by Lee Springer.
