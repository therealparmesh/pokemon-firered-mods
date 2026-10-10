# Pokémon FireRed Mods

FireRed and LeafGreen with an in-game mod menu. Change encounters, give items, edit your party, adjust battle effects, or use world tools without entering external codes.

This is a fork of [pret/pokefirered](https://github.com/pret/pokefirered). It supports **English revision 0** of both games.

## Play

Download the matching `.bps` patch from [Releases](https://github.com/therealparmesh/pokemon-firered-mods/releases) and apply it to your own lawfully obtained original ROM with a BPS patcher, such as [Floating IPS](https://github.com/Alcaro/Flips). Releases do not include complete ROMs.

The original files must have these SHA-1 hashes:

| Game | SHA-1 |
| --- | --- |
| FireRed | `41cb23d8dccc8ebd7c649cd8fbb58eeace6e2fdc` |
| LeafGreen | `574fa542ffebb14be69902d1d36f1ec0a4afd71e` |

## Open the menu

Stand still, **hold Start first, then tap Select**. Release both buttons before using the menu. Do not hold Select first: Select alone activates the game's registered item and may open a dialog that blocks the shortcut.

You can also press **Start → Mods → A**. Mods is available in the normal and Safari Start menus, but not during battles, dialogs, link play, or Quest Log playback.

- **Up/Down:** choose a row.
- **Left/Right:** change the selected value. Named choices skip unused or disallowed entries and wrap at the ends. Holding a direction repeats.
- **L/R:** move by ten numbers or valid choices; stop at the ends.
- **A:** open a category or browser, select a choice, or run an action.
- **B:** cancel, go back, or close the menu.

Inside a browser, **Select** changes the region, item pocket, or move type; **Start** switches between ID and alphabetical order. Left/Right and L/R page by ten entries.

On Main, choose **Active mods** or press Select to see enabled effects. A disables the highlighted effect and removes its row. Start offers to disable them all; A confirms and B cancels. You can enable them again in their categories.

Party edits take effect only after **Apply**. Runtime settings reset when you restart the game. Disabling mods does not undo items you gave yourself, Pokémon edits, or saved world changes. Back up your save before using those tools, especially story flags.

## Build locally

On macOS, install Homebrew and Xcode Command Line Tools first. On Debian/Ubuntu or WSL, setup reports any missing packages.

```sh
make setup
make roms
# The same build can be started with ./scripts/build-roms.sh
```

Setup can be run again safely. The build uses pret's compiler and build rules and produces:

```
dist/Pokemon-FireRed-Mods.gba
dist/Pokemon-LeafGreen-Mods.gba
```

No original ROM download or dump is needed for source builds. Generated ROMs stay local and are ignored by Git.

Use `./scripts/build-roms.sh --firered` or `--leafgreen` for one game, `--clean` for a clean rebuild, and `JOBS=4` to set compilation parallelism. `make clean` removes generated files; `make baseline` checks that unmodified builds match the original games. Homebrew users can use `gmake` if Apple's Make is too old.

`make patches` builds both games, runs the emulator tests, creates the BPS patches, and checks that applying each patch reproduces its tested ROM exactly. Building ROMs again removes old patches and release metadata.

## Testing and details

Builds check ROM headers and run input-driven mGBA tests when the setup-created emulator is present. Failed builds return a nonzero status and remove the selected outputs. Logs are in `logs/`; screenshots and test results are in `tests/output/`.

See [IMPLEMENTATION.md](IMPLEMENTATION.md) for feature details and coverage, [PUBLISHING.md](PUBLISHING.md) for releases, and [INSTALL.md](INSTALL.md) for pret's original build instructions.

Physical GBA hardware and an actual iPhone emulator have not been tested. Arbitrary story-flag changes can still break progression.
