# Implementation and verification

The project builds complete English revision 0 FireRed and LeafGreen images through pret's original Make rules. Native integration is in `src/mods.c`, `src/mod_menu.c`, `include/mods.h`, and the game hooks that call them. Build configuration uses `MODS=1`; `MODS=0` reconstructs the original games. No original ROM input, post-build patching, external code injection, or save-layout changes are required.

## Menu and state behavior

Hold Start and tap Select in idle field gameplay, or press Start, choose Mods and press A. The shortcut uses the native Start-menu path, including short simultaneous presses latched during drawing; only menus with a Mods entry allow it. Opening keys must be released before navigating the mod menu. Raw button handling preserves native L=A options and avoids the Help overlay. Seven visible rows, row counters, retained parent selections, and contextual status text fit the native 240×160 screen.

Pokémon browsers filter by region, item browsers by pocket, and move browsers by type. Select cycles filters; Start switches ID/A–Z order; L/R pages by ten. Filters and sorting preserve eligible highlighted IDs, and B cancels without changing the committed selection. Empty move/held-item choices remain first. Held-item lists exclude keys and mail. Browser allocations are released on selection, cancellation and close.

Single-step numeric edits wrap at both ends; ten-step jumps clamp like native shop quantity jumps. Held directions use the unchanged native input-repeat mechanism. Party bounds use the occupied slot count.

Main shows an enabled-effect count and an Active mods entry. Select on Main opens the same review without reusing the opening A press. The review lists each enabled runtime setting once, including settings shared by categories. Default EXP 1×, selection parameters, manual actions and party drafts do not count as ongoing effects.

A disables and removes the highlighted effect from the active list; B returns to Main; Start requests bulk disable with A/B confirmation. EXP disable restores 1×. Row removal keeps the cursor valid, and an empty state explains when no effects remain. Disable preserves selected parameters, drafts and custom shop stock. It does not undo grants, Pokémon edits, captures or world changes. Effects can be enabled again from their category. Power cycling resets session settings. Restore an earlier save to undo persistent changes that the menu cannot reconstruct.

Party edits are drafts until Apply. Validation checks usable slots, encrypted checksums, supported abilities, move/item validity and EV limits. Personality changes reorder and re-encrypt substructures. Unrelated edits preserve earned EXP, personality, HP, PP and PP Up bonuses; changed moves reset only their own PP/bonus.

Battle modifiers bypass link, tutorial and facility contexts. Wall traversal preserves native object interactions, ledges, Surf transitions and map bounds. Teleports require starter progression; Dex completion requires the Pokédex. Arbitrary story-flag edits remain inherently capable of producing inconsistent game state.

## Executed acceptance coverage

The controller-driven mGBA 0.10.5 runner starts from erased flash, completes the original new-game flow and reads RAM only for assertions. Extended branches load checkpoints created by that exact ROM during the same run. No RAM-write command or foreign save fixture is used.

The current suite contains **302 assertions per game**: 222 base/battle/world/browser assertions, 24 active-review assertions and 56 numeric/access-control assertions. Exact assertion names and tested ROM hashes are generated in `tests/output/<variant>/results.json`.

| Required acceptance | Verification |
|---|---|
| Both complete ROMs generated | One-command build publishes the two stable names in `dist/` |
| Title boot and normal gameplay | Original startup, introduction, naming, field movement |
| Menu opens and closes | Start-menu entry and Start+Select shortcut, Main landing, opening-key release, B close, all three native button modes |
| Real mods work and gameplay continues after disable | Bag grants, valid party/wild edits, real battles and restoration of ordinary effects |
| Save remains playable | Native flash save, power-cycle and Continue with preserved party/items |
| Rebuild after changes updates outputs | Hashes compared against the preceding revision |
| Clean rebuild succeeds | `./scripts/build-roms.sh --clean` runs both full suites before publication |
| Incremental rebuild is reproducible | Linked images compared byte-for-byte with the tested clean outputs |

Coverage includes all 20 heal-destination teleports, last-heal teleport, Oak/Koga progression, flag set/clear/cancel, Dex mirrors, grass encounters on/off, native ledges, Surf mounting/dismounting/teleport, status healing, recoil/self-KO, Substitute, Perish Song, Destiny Bond, Pressure, Spite and Grudge. Destiny Bond is checked while still live at the actual enemy KO, using a party fixture strong enough to avoid an intervening turn. Browser checks independently validate all 386 Pokémon name mappings, all item pockets, all move types including Curse, sort order, true IDs, safety exclusions and L=A paging.

Active-review checks cover all 11 runtime effects, shared-setting deduplication, EXP neutrality, individual removal, page boundaries, confirmation cancellation, bulk disable, parameter/draft/stock preservation, persistent party/items, repeated removal to zero, reopening, and subsequent ordinary movement.

## Integrity and failure behavior

Checks validate ROM size, Nintendo logo, game code, fixed header byte, header checksum, native build marker and linked menu/dialogue text. Both original baseline SHA-1 identities are checked:

- FireRed: `41cb23d8dccc8ebd7c649cd8fbb58eeace6e2fdc`
- LeafGreen: `574fa542ffebb14be69902d1d36f1ec0a4afd71e`

A build lock prevents concurrent pipelines. Selected stale outputs and the old manifest are removed before prerequisite checks. ROMs are staged and published only after selected variants pass. Missing-prerequisite failure cases cover both games and each single-game flag, including output/manifest/lock cleanup.

The source uses mod terminology throughout current project files; original Git history and third-party dependency identities are retained. Two trainer lines use “play fair” in mod builds while baseline-only game-encoded bytes preserve original checksums. Dead-code cleanup was restricted to our added code. The removed write-only action counter was introduced in our new mod files; no upstream function or asset was removed as dead code. The retired field-opening hook was also our own addition. Removed upstream lines were inspected for integration edits (guards/punctuation), branding comments and dialogue, rather than unrelated deletions.

## Evidence and limits

Fresh-checkout evidence lives in `logs/v1-final-patches.log`, `logs/release-refresh-clean.log`, `logs/emulator-<variant>.log`, `logs/v1-final-verification.json` and the per-game result JSONs. Native-resolution menu and browser screenshots are generated alongside those results.

Passing the covered suite is not an exhaustive guarantee for every combination of species, items, moves, story flags, terrain, link/facility state or historical saves. Physical GBA hardware is untested. Hosted CI status is visible on the repository's Actions page; local success does not imply a hosted run has passed.

Public releases contain only BPS patches and verification metadata. `make patches` uses pinned Floating IPS, validates exact original identities, runs both emulator suites, and checks that patch application reproduces each tested image byte for byte. Complete modified ROMs and original baselines remain ignored local outputs. ROM builds invalidate stale patches and release metadata.
