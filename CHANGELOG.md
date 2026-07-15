# Changelog

## v1.3.0-auto (2026-07-15)

- Slimmed the module from 5.9 MB to 3.5 MB with no rendering change:
  - `GoogleSansVF.ttf` (4.7 MB → 0.5 MB): subset to its actual job — the
    Cyrillic/Greek fallback, plus the combining marks, punctuation, and
    currency signs that appear inside those scripts. The ~2,400 characters
    it never rendered (Google Sans Flex always wins Latin) are gone, and
    the unused `GRAD` axis is pinned.
  - `RobotoFB.ttf` (2.4 MB → 1.3 MB): unused `wdth` axis pinned. All 2,797
    characters are kept.
- `Font.ttf` itself is untouched: Android 16's lock-screen clock animates
  its `GRAD`/`ROND` axes and Gecko drives `opsz`, so the main font must
  keep all six variation axes.

## v1.2.3-auto (2026-07-12)

- Fixed tofu for characters that stock Roboto covered but neither Google
  Sans Flex nor Google Sans has — ~1,600 codepoints, notably combining
  marks (e.g. the U+0336 strikethrough trick common in social-media
  titles), modifier letters, and extended Latin/Cyrillic/Greek. The
  device's stock Roboto now ships as `RobotoFB.ttf`, registered as a
  safety-net fallback family in both font configs.
- The bundled Roboto is internally renamed to `RobotoFB` so Gecko browsers
  keep resolving the `Roboto` family to Google Sans Flex.

## v1.2.2-auto (2026-07-09)

- `Font.ttf` is now the official Google Sans Flex v4.005 with only the
  internal rename to Roboto. An on-device A/B test confirmed the rename
  alone fixes the Gecko rendering bug — the earlier defensive extras
  (STAT Regular instance, no-op `smcp`/`c2sc` small-caps features) were
  unnecessary and are gone, along with ~50 KB of duplicate glyph data.
- `patch_font.py` simplified accordingly (rename-only).
- No behavior change on device; Cyrillic/Greek fallback and italics are
  unchanged from v1.2.1.

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
