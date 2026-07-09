# Changelog

## v1.2.1-auto (2026-07-09)

- Fixed Cyrillic/Greek text rendering as boxes (tofu): Google Sans
  (`GoogleSansVF.ttf`, same superfamily, full Cyrillic incl. Ukrainian +
  Greek) is now bundled and registered as the first system fallback family.
- The fallback family is registered in `/system/etc/font_fallback.xml` — the
  config Android 13+ actually reads — as well as the legacy `fonts.xml`.
- Real oblique italics: config entries now instantiate the font's `slnt`
  axis (stock declares an `ital` axis Google Sans Flex doesn't have, so
  italics rendered upright).
- Explicit `wght`/`slnt` axis values for the masked NotoSerif bold/italic
  entries (they otherwise render at the variable-font defaults).
- Upgraded the main font to the official Google Fonts Google Sans Flex
  v4.005 build.
- Per-component licensing: `LICENSE` index at the repo root; fonts under
  SIL OFL 1.1, installer scripts under GPL-2.0 (inherited from
  MMT-Extended), font configs under Apache-2.0 (AOSP-derived),
  `patch_font.py` under GPL-3.0-or-later. All license texts ship in the zip.
- Installer cleanup: deduplicated font copy, fixed a stray `sed` backup
  artifact, fixed dangling product-partition symlinks, removed stale zip
  signature files.
- Magisk in-app updates via `updateJson`.

## v1.1.0-auto (2026-07-01)

- Initial public release.
- Google Sans Flex internally renamed to `Roboto` so Gecko (Firefox/Fennec)
  resolves the CSS `sans-serif` family correctly — fixes body text rendering
  as all-caps/small-caps on many sites.
- STAT `wght=400 Regular` named instance; no-op `smcp`/`c2sc` GSUB features
  so Gecko never synthesizes small-caps.
- Zero-prompt installer: full 20-weight Roboto set plus
  GoogleSans/DroidSans/ProductSans/NotoSerif compatibility symlinks.
