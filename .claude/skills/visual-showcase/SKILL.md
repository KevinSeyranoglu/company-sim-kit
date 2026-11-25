---
name: visual-showcase
description: Add an optional animated top-down view of a company simulation (pygame-ce) and record demo videos/GIFs for the README, keeping drawing fully separate from the simulation. Use when the user wants the simulation to be watchable or playable, or needs a demo GIF.
---

# Visual showcase (optional)

The animation sells the project in the first five seconds of the README, but the data is the product.
Build it after the data layer works, and never let it change the simulation's results.

## Architecture

- `renderer.py` and `ui.py` read the simulation's state; they never change it. The game loop advances
  the simulation and draws. Headless runs never import pygame.
- The event-driven starter needs positions for drawing: add a light `positions(t)` method that
  interpolates each moving entity between its last two events (start and end of a task), instead of
  adding a time-stepped engine.
- Speeds 1×–20×; at 1× one simulated hour is about one real minute. Pause, pan, zoom, click to inspect.
- Draw with shapes and text only (no image or sound files, nothing copyrighted). Colour-code zones and
  roles; show live KPIs in a sidebar.
- Add `pygame-ce` to `requirements.txt` and set `SDL_VIDEODRIVER=dummy` in CI.

## Recording

A `--record docs/demo.mp4 --hours 24 --speed 20` option renders offscreen; convert a short segment to a
GIF with ffmpeg (`palettegen` / `paletteuse`, 12–15 fps, under 8 MB) for the README.

## Tests

A test that runs the game loop for a few hundred frames with the dummy video driver and checks the
simulation's data is identical with and without the renderer.
