# MCG Netherfall

A 2D top-down roguelike survival game built with Python and Pygame — survive endless waves of enemies, level up abilities, and take down bosses across increasingly chaotic runs.

## Features

- **2 playable characters** (Ranger, Gigachad), each with their own stats and ability set
- **Ability system**: burning, poison, healing, shield and invincibility abilities, upgradeable via a skill tree
- **Enemy variety**: bats, blobs, skeletons and 2 unique bosses, with escalating waves the longer you survive
- **Power-ups and XP progression** collected mid-run
- **Persistent saves** (achievements, unlocked skills/stats) via `SaveManager`
- **Multi-language UI**: English, Spanish and Portuguese (`translations/`)
- **Custom tile-based maps** and a dedicated sound/music manager

## Tech stack

Python + [Pygame](https://www.pygame.org/). No external services — fully self-contained, runs locally.

## Project structure

```
main.py            # entry point — game loop wiring, character selection, reset flow
managers/          # EnemyManager, GameManager, SaveManager, MusicManager, SoundManager, PowerupManager
characters/         # Character base class, Ranger, Gigachad
enemies/            # Enemy base class, bat/blob/skeleton, 2 bosses
abilities/          # Ability base class + burning/poison/healing/shield/invincibility
ui/                 # Menu, loading screen, UI utilities
tiles/              # Tile-based map rendering
translations/        # en.json, es.json, pt.json
assets/             # sprites, sounds, backgrounds
save/               # save.dat — persisted player progress
```

## Running it

```bash
pip install pygame
python main.py
```

## Roadmap

A browser-playable build (via [pygbag](https://github.com/pygame-web/pygbag), which compiles Pygame to WebAssembly) is planned for the portfolio site — not for this repository directly.
