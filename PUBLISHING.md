# Contributing and releases

Work on `native-mods` in [pokemon-firered-mods](https://github.com/therealparmesh/pokemon-firered-mods). Keep the original [pret/pokefirered](https://github.com/pret/pokefirered) history and attribution. Our commits use Conventional Commits, for example `fix: skip unused item IDs while scrolling`.

Run `make setup` and `make roms` before submitting a change. The source and tool revisions are pinned in `config/dependencies.env`; updating upstream or the compiler requires checking both games again.

## Publish a release

1. Run `./scripts/build-roms.sh --clean`, `make patches`, and `python3 tests/pipeline_failures.py`.
2. Check both emulator result files and patch round trips. Compare incremental ROMs with the clean builds.
3. Commit and push. Check the fresh Linux workflow separately from local results.
4. Tag the tested commit and attach only the two `.bps` patches, `patches.json`, `verification.json`, and `SHA256SUMS`.
5. Describe the changes, checks actually performed, and anything still untested.

**Do not upload complete ROMs, original baselines, saves, or emulator states.** Keep generated files out of Git. The three tracked `data/mb_*.gba` files belong to upstream and are small multiboot payloads needed by its build.

Actions builds and tests both games and patches, but does not publish anything. Release tags do not start another copy of the branch workflow. Existing Actions runs can be deleted after recording their verified result; the workflow remains available for later changes.

## Distribution

A public decompilation or a successful build does not grant permission to redistribute the original game. Patches reduce the amount of original material distributed but are not a guarantee of legal permission. Respect copyright and takedown requests. See the [U.S. Copyright Office](https://copyright.gov/what-is-copyright/) and [GitHub's DMCA policy](https://docs.github.com/en/site-policy/content-removal-policies/dmca-takedown-policy).

Keep README focused on player controls and build steps. Put engine details and test evidence in IMPLEMENTATION.md.
