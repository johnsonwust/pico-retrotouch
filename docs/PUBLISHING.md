# Publishing this source snapshot

[Project overview](../README.md) · [Documentation](wiki/Home.md)

This is prepared as a **source-only** repository. The workspace's personal firmware/recovery packages are not public releases.

1. Review the tracked source list with `git diff --cached --stat` / `git ls-files`.
2. Run `python scripts/audit_public.py` before each upload. Its content checks are an aid, not a complete license/security audit.
3. Keep `local-assets/`, `build/`, `dist/` and `external/` out of Git and downloadable archives. A folder being ignored by Git does not stop someone manually uploading it elsewhere.
4. Retain the license map, original notices, fixed dependency revisions and build scripts. Do not label all native dependencies MIT. Review actual GPL versions and complete corresponding source if ever distributing a linked executable.
5. Keep user ROMs, OS/application disks, games, memory dumps, private keys and token-bearing logs out of commits, Releases, Pages and CI artifacts. No workflow here publishes build artifacts. PNG screenshots are allowed only when listed by hash in the reviewed `docs/screenshots/captures.json`; this does not turn displayed third-party artwork into open-source assets.
6. Public native firmware is deliberately not supplied because this build embeds a locally supplied ROM. An SD-loaded-ROM design would be a separate feature and still needs distribution/compliance review.
7. Update `docs/VERIFICATION.md` when hardware-testing the public font/artwork variant. Don't present the private prototype's physical tests as tests of newly changed public firmware.

Git commit history and attachments need review too; deleting a file in a later commit does not remove earlier copies. Prefer this clean repository over pushing the original development directory.

## Publication root and archive

Publish this clean source repository, not the surrounding prototype development workspace. Build source archives from the reviewed Git index or commit, so ignored ROMs, runtime disks, local dependencies and private logs cannot be pulled in by a recursive folder ZIP. Check the archive entry list before uploading it.

The owner has authorized publication of the English source and documentation to GitHub. The future Tindie listing is a separate step; its draft is included for review, not as a live product offer. The [software sources page](SOFTWARE-SOURCES.md) records third-party references without bundling their downloads. Blog photographs remain linked at the author's site.

The project is independently branded. Names such as Macintosh and Finder are compatibility references; original Apple assets and games are not relicensed by this repository. See LICENSE.md and THIRD_PARTY_NOTICES.md.
