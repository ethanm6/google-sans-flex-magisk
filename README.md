# UnFont — Google Sans Flex for Android (Magisk module)

Systemlessly replaces the Android system font with **Google Sans Flex**
(official v4.005), patched so it renders correctly in Firefox/Gecko-based
browsers. **Google Sans** is bundled as the fallback for Cyrillic and Greek
(scripts Google Sans Flex doesn't cover), registered in the system font
configs — `font_fallback.xml`, the one Android 13+ actually reads, plus the
legacy `fonts.xml` — so mixed-script text keeps a consistent Google Sans
look, and italics use the font's real `slnt` axis. Stock **Roboto** also
rides along (as `RobotoFB.ttf`) as a last-resort fallback for the ~1,600
characters neither Google font covers — combining marks, modifier letters,
extended Latin/Cyrillic/Greek — so nothing that rendered before the module
turns to tofu under it. Installs with zero prompts; updates are offered in
Magisk directly.

- Module ID: `UnFont`
- Target environment: LineageOS, Android 16

---

## Credit

This module is forked from **[AndroSYNC](https://github.com/AndroSYNC)**'s
font module, built on the **OMF / MMT-Extended** installer template.
All installer scaffolding — `common/functions.sh`, the MMT-Extended
`customize.sh` template, and the multi-weight symlink installer pattern —
originates there. This fork's contribution is the font patch and a
streamlined, no-prompt installer that removes the ROM-selection menu.

The fonts are **Google Sans Flex** and **Google Sans**, © Google, both
published on [Google Fonts](https://fonts.google.com/specimen/Google+Sans+Flex)
under the SIL Open Font License 1.1 — see `LICENSE-OFL.txt`, which the OFL
requires to accompany the fonts.

---

## The bug this fixes

In Fennec (Firefox for Android), body text on many sites rendered as
all-caps / small-caps even though Android's own UI looked normal. Gecko
resolves the CSS `sans-serif` generic by the font's *internal* family name
and expects `Roboto`; with a font internally named "Google Sans Flex" it
silently fell back to its bundled Fira Sans, which produced the small-caps
appearance. Android's renderer matches fonts by file path instead, which is
why the bug looked web-only.

**Fix:** the font's `name` table is patched so the family resolves as
`Roboto` — that is the entire patch. (Earlier versions also added a STAT
Regular instance and no-op small-caps features as defensive measures; an
on-device A/B test showed the rename alone is sufficient, so they were
dropped.)

---

## Installing

1. Download the zip from the [Releases](../../releases) page.
2. Flash it in Magisk Manager.
3. Reboot.

The module installs the full 20-weight Roboto-named set (required by Gecko)
plus GoogleSans / DroidSans / ProductSans / NotoSerif compatibility
symlinks — all pointing at the single patched `Font.ttf`, with the real
`GoogleSansVF.ttf` (Cyrillic/Greek fallback) and `RobotoFB.ttf` (last-resort
safety net) alongside.

---

## Rebuilding

The Google fonts come from Google Fonts (find the current variable-TTF URLs
via `https://fonts.google.com/download/list?family=Google%20Sans%20Flex` and
`...family=Google%20Sans`).

`files/Font.ttf` is the Google Sans Flex variable TTF run through
`patch_font.py` (which self-checks on exit; requires
[fonttools](https://github.com/fonttools/fonttools)):

```bash
pip install fonttools
python3 patch_font.py GoogleSansFlex.ttf files/Font.ttf
```

Don't strip or pin any of `Font.ttf`'s six variation axes: Android 16's
lock-screen clock animates `GRAD`/`ROND`, Gecko drives `opsz` for optical
sizing, and the font configs use the rest.

`files/GoogleSansVF.ttf` is the Google Sans variable TTF, subset to its
fallback role — Cyrillic, Greek, combining marks, and the punctuation and
currency ranges that appear inside those scripts — with the unused `GRAD`
axis pinned (4.7 MB → 0.5 MB):

```bash
pyftsubset GoogleSans.ttf \
  --unicodes="U+0020-007E,U+00A0-00FF,U+0300-036F,U+0370-03FF,U+1F00-1FFF,U+0400-04FF,U+0500-052F,U+1C80-1C8F,U+2DE0-2DFF,U+A640-A69F,U+2000-206F,U+20A0-20CF,U+2116" \
  --layout-features='*' --name-IDs='*' --notdef-outline \
  --output-file=GoogleSans-subset.ttf
fonttools varLib.instancer GoogleSans-subset.ttf GRAD=0 -o files/GoogleSansVF.ttf
```

`files/RobotoFB.ttf` is a stock Android Roboto variable TTF (e.g. from
[roboto-classic](https://github.com/googlefonts/roboto-classic)) with its
internal family renamed to `RobotoFB` and the unused `wdth` axis pinned
(`fonttools varLib.instancer Roboto.ttf wdth=100`); all its characters are
kept. The rename matters: a font still internally named `Roboto` would make
Gecko resolve the `Roboto` family to it instead of Google Sans Flex,
reintroducing the bug this module fixes.

`files/fonts.xml` and `files/font_fallback.xml` are the stock LineageOS /
AOSP font configs with the Google Sans fallback family inserted first in
the fallback list, `ital` axis references replaced with the font's real
`slnt` axis, and explicit axis values on entries whose stock file the
module masks. If your ROM's stock configs differ significantly, re-apply
those edits to your device's own copies.

To package the flashable zip (run from the repo root; repo-only files are
excluded — they aren't part of the module):

```bash
zip -r ../Google_Sans_Flex.zip . \
  -x ".*" -x ".git/*" -x "README.md" -x "patch_font.py" \
  -x "CHANGELOG.md" -x "update.json"
```

---

## Licensing

Each component keeps its own license — see the [`LICENSE`](LICENSE) index
for the full mapping and copyright notices. In short:

- **Fonts** (`Font.ttf`, `GoogleSansVF.ttf`, `RobotoFB.ttf`) — SIL Open
  Font License 1.1
  ([`LICENSE-OFL.txt`](LICENSE-OFL.txt)). The OFL requires the fonts to stay
  under the OFL.
- **Installer scripts** — GPL-2.0 ([`LICENSE-GPL2.txt`](LICENSE-GPL2.txt)),
  inherited from the [MMT-Extended](https://github.com/Zackptg5/MMT-Extended)
  template they derive from.
- **Font configs** (`fonts.xml`, `font_fallback.xml`) — Apache-2.0
  ([`LICENSE-Apache2.txt`](LICENSE-Apache2.txt)), derived from AOSP /
  LineageOS.
- **`patch_font.py`** — GPL-3.0-or-later
  ([`LICENSE-GPL3.txt`](LICENSE-GPL3.txt)).

---

## Support

If you find this project useful, you can support development:

[![Support me on Ko-fi](https://ko-fi.com/img/githubbutton_sm.svg)](https://ko-fi.com/ethanm6)

---

## Disclaimer

This project is unofficial and is not affiliated with or endorsed by Google.
It is provided **as-is**, without warranty of any kind — the component
licenses above carry the full warranty and liability disclaimers. Flash at
your own risk: modules that patch system fonts can affect device stability.
