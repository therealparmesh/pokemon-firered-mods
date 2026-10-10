# Repository and releases

The project uses the original pret history plus our commits on `native-mods`. The public GitHub fork is [therealparmesh/pokemon-firered-mods](https://github.com/therealparmesh/pokemon-firered-mods), upstream [pret/pokefirered](https://github.com/pret/pokefirered). Public forks remain public; an independent private repository is an alternative when private visibility is needed. [GitHub fork documentation](https://docs.github.com/en/pull-requests/reference/forks).

## Contributing

```sh
git switch native-mods
make setup
make roms
git add <changed-source-files>
git commit -m "fix: describe the change"
git push origin native-mods
```

`origin` should point to our fork and `upstream` to pret. Keep pret attribution and history. Our commits use Conventional Commits (`feat:`, `fix:`, `docs:`, `test:`, or `chore:`). The initial 1.0 feature commit is directly atop the pinned pret revision; upstream history is not rewritten. Do not sync or rebase onto a new upstream revision without rebuilding and verifying both games; the initial source/compiler/emulator revisions are in `config/dependencies.env`.

## Release process

1. Complete source/documentation review and run a clean one-command build, `make patches`, and the failure-cleanup checks.
2. Check that both `dist/` ROM hashes equal the hashes in their current emulator result JSONs. Compare incremental builds against the tested clean images.
3. Commit and push the source. Check the hosted Actions run separately from local results.
4. Create a versioned GitHub Release tied to the exact source commit and attach only the two `.bps` patches, their input/output hash manifest, SHA-256 checksums, and a verification report. Never attach complete ROMs, original baselines, saves, or emulator states. Keep local build artifacts out of Git.
5. Describe native menu controls, the supported English revision, executed checks, and hardware/coverage limitations in the release notes.

`dist/`, `.build-deps/`, `logs/`, `tests/output/`, `roms/`, saves and generated binaries stay ignored. The tracked `data/mb_*.gba` files are upstream multiboot payloads required for compilation. They are not full FireRed/LeafGreen play builds.

The read-only Actions workflow installs prerequisites, builds pinned tools, checks both original baselines, builds both modified games and BPS patches, and runs both full emulator suites, patch round-trip checks and failure cleanup. It does not automatically upload ROMs or create releases. Releases are published explicitly after review. If Actions is disabled on a new fork, enable it before relying on hosted CI.

## Upstream and distribution

Checked on 2026-10-09: upstream has no GitHub releases. Its README's ROM links are No-Intro identity records rather than downloads. Its tree contains three small multiboot payloads. [Upstream repository](https://github.com/pret/pokefirered), [upstream releases](https://github.com/pret/pokefirered/releases).

Compiling from source and creating a fork do not establish copyright permission to redistribute the underlying game. Release upload capability is separate from permission from relevant rights holders; respect applicable rights and any takedown requests. [U.S. Copyright Office guidance](https://www.copyright.gov/help/faq/faq-fairuse.html), [GitHub DMCA policy](https://docs.github.com/en/site-policy/content-removal-policies/dmca-takedown-policy).
