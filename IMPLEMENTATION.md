# Engine notes and test coverage

Both English revision 0 games use the same mod engine. The code lives in `src/mods.c`, `src/mod_menu.c`, and `include/mods.h`, with hooks in the original game systems. `MODS=1` enables those hooks; `MODS=0` builds the originals. Nothing is patched into the ROM after compilation, and the save layout is unchanged.

## Menu behavior

Named choices use National Dex numbers, defined item IDs, and the game's move table. Left/Right walks those choices, skipping unused items and excluding key items and mail from held-item choices. Single steps wrap; ten-choice jumps stop at the ends. A opens the browser. Scrolling does not open it implicitly.

Browsers offer region, pocket, or move-type filters and ID/A–Z order. Changing the filter or order keeps the highlighted choice when possible. None remains first for moves and held items. B cancels without changing the committed choice, and browser allocations are freed on selection, cancellation, or close.

The Start+Select shortcut follows the native Start-menu path. Start must come first so Select does not activate a registered item. A short combined press is remembered while the Start menu draws, and opening buttons must be released before they can operate Mods. The shortcut is available only where the Mods entry is available.

Active mods lists enabled runtime effects once, even when two categories share a setting. It excludes selection parameters, party drafts, and neutral EXP 1×. Disabling a row removes it and keeps the cursor in bounds; disabling EXP restores 1×. Bulk disable asks for confirmation. Neither operation undoes permanent save edits.

## What the engine changes

- Wild Pokémon: species, level, shiny state, nature and IVs, plus explicit give/encounter actions. The special Tower ghost and tutorial creation paths remain separate.
- Items: bag grants, quantity, eight-entry shop stock, free purchases and money protection. Native bag capacity and shop restrictions still apply.
- Party: species, level, nature, supported ability, shiny state, friendship, held item, IVs, EVs and moves. Apply validates the draft, recalculates stats and preserves unrelated data. EV limits are 252 per stat and 510 total. Personality changes re-encrypt and reorder the original substructures.
- Battles: HP and PP protection, wild capture, EXP and encounter controls. Link, tutorial and facility battles bypass these effects. Native trainer and ghost capture restrictions remain.
- World: healing, walking speed, bounded wall traversal, last-heal and 20 named teleports, Dex flags and story flags. Teleports require a starter; Dex completion requires the Pokédex. Arbitrary story flags can still break progression.

## Tests

The pinned mGBA runner starts a new game with erased flash and uses controller input to reach gameplay and operate the menu. Later scenarios load checkpoints created by that exact ROM during the same run. RAM is read for assertions, including independent Pokémon checksum/encryption checks; the runner does not write RAM or load foreign saves.

Coverage includes title boot, new-game flow, movement, saving and Continue; mods on/off; all 20 teleport destinations; Oak and Koga progression; Dex completion; grass encounters; ledges and Surf; and real battle effects including recoil, Substitute, Perish Song, Destiny Bond, Pressure, Spite and Grudge.

List tests cycle both directions through every bag item, permitted held item, species choice and move in all four slots. They check wrapping, ten-choice jumps and that scrolling stays on the parent screen. Shortcut tests cover all three button modes, brief taps, menu-drawing timing, opening-key release, native Start/Select behavior and rejection during battles/dialogs.

Each game writes its assertion names and ROM hash to `tests/output/<game>/results.json`, with screenshots alongside it. `logs/` contains local build diagnostics. Release `verification.json` records the tested source commit and results.

## Build and release checks

Builds check the header, Nintendo logo, game code, size and native marker before publishing local outputs. Original builds must match the SHA-1 files checked into the repository. Missing prerequisites and failed verification return nonzero and remove selected stale outputs; tests cover both games and each single-game flag, including stale patch metadata.

`make patches` uses pinned Floating IPS, applies each BPS patch to the exact original baseline and compares the result byte for byte with the emulator-tested ROM. Public releases include patches and metadata only. Full ROMs, baselines, saves and emulator states remain ignored local files.

Original upstream history and required assets are retained. Dead-code cleanup is limited to our additions. Physical GBA hardware and an actual iPhone emulator have not been tested; the automated coverage does not exhaust every story state or historical save.
