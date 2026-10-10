# Native mods for Pokémon FireRed and LeafGreen

A source fork of [pret/pokefirered](https://github.com/pret/pokefirered), pinned initially to `037335f4c725d7c9aecdac87066f2002b4bd7e14`. Both English revision 0 games share one native C mod engine. The original game, assets, scripts, music, saving, and compilation rules are retained.

## Play

[GitHub Releases](https://github.com/therealparmesh/pokemon-firered-mods/releases) provide **BPS patches only**, not complete game ROMs. Apply the matching patch to your own lawfully obtained English revision 0 FireRed or LeafGreen dump with a BPS-compatible patcher such as [Floating IPS](https://github.com/Alcaro/Flips). The required original SHA-1 identities are:

- FireRed: `41cb23d8dccc8ebd7c649cd8fbb58eeace6e2fdc`
- LeafGreen: `574fa542ffebb14be69902d1d36f1ec0a4afd71e`

Alternatively, build both complete games locally using the command below. No original dump or ROM download is needed for source builds. Generated ROMs remain ignored local files.

In normal field gameplay, stand still, hold Start and tap Select to open the native menu. Start → Mods → A remains available. Select on Main reviews enabled effects; A disables and removes a highlighted effect from that list; B returns/back closes the menu. Effects remain available in their category for re-enabling. Keep a save backup before persistent item, party or world edits. Physical hardware is untested.

## Build

On macOS, install Homebrew and Xcode Command Line Tools once. On Debian/Ubuntu (including WSL), install the prerequisites printed by setup. Then, from this repository:

```sh
make setup
./scripts/build-roms.sh
# Equivalent:
make roms
```

On Homebrew systems, `gmake` can be used if `make` is an older Apple-provided version. Setup installs/checks ARM binutils, the host C/C++ toolchain, libpng, Python 3, Perl, Git, pkg-config, and CMake. It builds the pinned pret agbcc compiler and pinned mGBA 0.10.5 headless library locally. No GUI emulator is required. Setup can be repeated safely; logs live in `logs/`.

Successful builds publish:

```
dist/Pokemon-FireRed-Mods.gba
dist/Pokemon-LeafGreen-Mods.gba
dist/manifest.json
```

The `.gba` files are complete ROM images that can be loaded directly in mGBA. They are generated locally and remain excluded from Git; published play builds, when available, are attached to GitHub Releases. Physical hardware compatibility has **not** been tested.

```sh
./scripts/build-roms.sh --firered      # FireRed only
./scripts/build-roms.sh --leafgreen    # LeafGreen only
./scripts/build-roms.sh --clean        # clean and rebuild both
make clean                           # remove build products/assets/tools and dist
make verify                          # integrity and input-driven mGBA tests
make baseline                        # MODS=0; require exact upstream SHA-1s
```

The native feature uses `MODS=1` by default and `NATIVE_MODS` in source. Project files, UI labels, build outputs and publishing instructions use mod terminology. Git history and third-party dependency APIs retain their original identities.

`JOBS=4 ./scripts/build-roms.sh` controls parallel compilation. Both variants have separate object directories. Switching between baseline and mod builds invalidates object files automatically. Incremental builds scan source/header/asset dependencies using pret's existing tools. Setup/build configuration and immutable compiler/emulator source revisions are checked in. The manifest records host tool versions, a digest of `src/` and `include/`, and ROM hashes; clean rebuilding with the same toolchain is byte-reproducible.

The build script stages both outputs and verifies them before publication. A failure removes selected outputs and returns nonzero, including emulator failures. Concurrent build scripts are rejected. A killed process may leave `.build-deps/rom-build.lock`; remove that empty directory only after confirming no build is running. Successful integrity checks cover the complete Nintendo logo, game code, fixed header byte, header checksum, and ROM size. The complete base and extended emulator suites run automatically when the setup-created headless driver is present; without it, the script reports verification unavailable. `make verify` requires the emulator driver and also exercises failure cleanup in disposable test repositories. Run `python3 tests/pipeline_failures.py` for those cleanup tests alone.

## ROM inputs

This pinned decompilation builds all required assets from the checked-in source and needs **no original ROM dump** or asset extraction. No ROM download is performed. Optional legally obtained reference dumps may be placed in ignored `roms/FireRed.gba` and `roms/LeafGreen.gba` and validated with:

```sh
python3 scripts/validate-reference-roms.py
```

Only English revision 0 reference dumps are accepted, with the upstream SHA-1 identities. References are optional and are never build inputs. The exact clean-baseline hash tests independently validate reconstruction.

## Release patches

Run `make patches` after `make setup` to build both exact original baselines, both modified games, and verified BPS patches in `dist/`. This configures a pinned Floating IPS CLI, runs the full emulator suites, and verifies both patch round trips byte for byte. Complete ROMs and baseline images stay local; publish only `.bps` patches and verification metadata. Rebuilding ROMs invalidates old patches and release metadata.

## Controls

During idle single-player field gameplay, press **Start**, choose **Mods**, and press **A**. Or use the two-button shortcut: **hold Start, then tap Select**. A simultaneous Start+Select press also works; Start first avoids activating a registered item. Release both buttons before navigating Mods. Mods is also available in the Safari Start menu; link/Union Room menus do not expose it. Native field restrictions still apply during movement, fades, scripts, battles and Quest Log playback. Mod navigation uses raw keys so the L=A option does not turn L/R paging into confirmation. Select alone retains its native registered-item behavior outside the mod menu. The shortcut is restricted to native Start menus that offer Mods; it does not run in battles or scripts.

- **Up/Down:** move through rows and scroll across pages.
- **Left/Right:** adjust a number or toggle a setting.
- **L/R:** adjust numbers or named browser positions by ten.
- **A:** choose a category, open a named browser, select an entry, toggle, or execute an action.
- **Select, inside a named browser:** cycle region, pocket or type filters.
- **Start, inside a named browser:** toggle native ID order / alphabetical A–Z order.
- **B:** cancel a browser/confirmation, return to the parent menu, or close the main menu.

Named browsers reopen at the committed selection in All/ID order. Pokémon filters cover Kanto, Johto and Hoenn Dex ranges; item filters use native bag pockets; move filters cover all 18 Gen III types, including Curse's “???” type. Filters and sorting keep the highlighted ID when it remains visible. None stays first for held items and moves; held-item filters skip key items and continue to exclude mail. Sorting uses case-insensitive displayed names.

The menu uses the game's own window, font, border, sound, task and field-lock APIs. Row counters show scroll position, named browsers distinguish selection from editing, and Back restores the parent selection. Party edits are drafts until Apply; the EV page shows the live total. Ability names are displayed, empty party slots cannot be selected, and held-item browsers exclude key items and mail. All configuration is session-only and resets at power-off or soft reset. Saving keeps legitimate item/Pokémon/world edits, but does not persist mod toggles. No save-structure fields were added. Main shows the number of enabled runtime mods. Choose Active mods or press Select on Main to review them. The review lists only enabled effects, without duplicating settings shared by categories; default EXP 1×, wild parameters and party drafts do not count as active effects. A disables the highlighted effect, B returns to Main, and Start requests bulk disable with A/B confirmation. Disabling EXP restores 1×. Removing an entry keeps the cursor valid, and an empty state explains when nothing is enabled.

“Disable all mods” turns off runtime modifiers while preserving selected parameters, party draft fields and custom shop stock. It does not undo already granted items, edited Pokémon, captured Pokémon or changed event flags. Closing and reopening the menu keeps the current session settings; power cycling resets them. The Start-menu entry is independent of the Select review shortcut. Numeric Left/Right edits wrap between their minimum and maximum, and held directions use the native configured initial delay and repeat cadence. L/R ten-step jumps clamp at the bounds, like native shop quantity jumps. Party slots wrap only across occupied slots.

## Features

- **Wild Pokémon:** named National Dex browser covering all 386 species, level 1–100, shiny encounters, random or selected nature, and random or uniform IVs 0–31. Wild battle entry points apply the modifiers after ordinary land, water, fishing, Rock Smash, roamer, and scripted legendary creation; disabling the override restores the engine's original selection logic. The special Pokémon Tower ghost and tutorials retain their dedicated creation paths. Explicit “Give selected Pokémon” and “Start selected encounter” actions also use the configured creation modifiers. Gifts honor nature and IV settings even with encounter override OFF. Giving refuses a full party; starting requires a conscious non-egg party member and enabled override, and is blocked in the Safari Zone.
- **Items/shop:** named browser of defined bag items, quantity selector, bag insertion through `AddBagItem`, and a native shop with up to eight chosen entries. Adding a ninth distinct stock entry replaces the oldest. Shop stock excludes key items and zero-price items, which the native purchasing UI does not support; those remain available through bag insertion. Free purchases show a zero price and respect bag capacity. Infinite money displays the native maximum and prevents spending, preserving the stored balance for later disablement.
- **Party editor:** selected slot, species, level, nature, species-supported ability slot, shiny state, friendship, held item, six individual IVs, six individual EVs, and four named moves. Apply recalculates stats; changing species or level updates experience, and replacing a move resets only that slot's PP and PP Up bonus. Unrelated edits preserve earned EXP, personality, current PP and PP Up bonuses. The IV and EV pages include all-31 and clear-all presets. EVs are limited to 252 per stat and 510 total. Eggs, bad eggs, missing slots, unsupported second abilities, key items as held items, and mail changes are refused. Personality changes preserve trainer ID and the gender-determining low byte (gender stays the same when species is unchanged) and reorder/re-encrypt the four substructures; they do not overwrite a personality word in isolation. Nickname, ribbons and other metadata remain intact.
- **Battle:** independently selectable HP damage prevention, PP preservation (including the Pressure, Spite and Grudge loss paths), guaranteed wild capture, EXP multiplier 1–10, no random encounters, and shiny wild generation. Link battles, tutorials, and battle facilities bypass battle modifiers. Trainer/ghost ball restrictions remain enforced. EXP is capped at the native 16-bit transfer limit. HP protection applies to the engine's HP update paths and direct attacker HP subtraction/self-KO paths; it does not revive Pokémon already fainted before battle.
- **Player/world:** heal party and status/PP, infinite money, faster walking, bounded wall traversal, teleport to the last heal location or the game's 20 heal destinations, seen/caught Dex flags, and story-flag set/clear (IDs 32–1279). Risky actions require a second A press with a save-first warning. Teleports require the story's starter flag; Dex actions require the Pokédex flag. Wall traversal keeps map bounds and object collision checks. Event edits can still create inconsistent story state; the confirmation is not a guarantee that an arbitrary flag combination is safe.

## Verification and limitations

See [IMPLEMENTATION.md](IMPLEMENTATION.md) for executed tests and remaining coverage. The automated runner uses only emulated controller inputs to initialize a new game, navigate menus and execute actions. Extended branches restore checkpoints created by that same ROM during the current test run; there are no foreign save fixtures or RAM writes. Coverage includes all 20 teleport destinations, normal progression through Oak and Koga, Pokédex completion, native grass encounter suppression/restoration, Surf transitions, status healing, and complex battle effects with modifiers enabled and disabled. It reads RAM for assertions and independently checks Pokémon encryption/checksums; it does not inject mod codes, change RAM, skip initialization or supply pre-made saves. PNG evidence and machine-readable results are generated in `tests/output/<game>/`.

The source foundation's upstream build documentation is retained in [INSTALL.md](INSTALL.md). Further regression testing remains appropriate for arbitrary event-flag combinations, every item/species/move, linked play, battle facilities, other maps, and user-supplied historical saves. Hardware testing requires a real compatible device.

## GitHub publishing

See [PUBLISHING.md](PUBLISHING.md) for the repository, release process and CI behavior.
