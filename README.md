# UnFont — Google Sans Flex for Android (Magisk module)

Systemlessly replaces the Android system font with **Google Sans Flex**
(official v4.005), patched so it renders correctly in Firefox/Gecko-based
browsers, with **Google Sans** bundled as the Cyrillic/Greek fallback.
Installs with zero prompts.

- Module ID: `UnFont`
- Version: `v1.2.1-auto`
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

**Symptom:** In Fennec (Firefox for Android), body text on many sites
(Wikipedia, GitHub, Google, etc.) rendered as all-caps / small-caps,
even though Android's native UI looked completely normal.

**Root cause:** Google Sans Flex's internal font family name is literally
"Google Sans Flex". Gecko (Firefox's rendering engine) resolves the CSS
`sans-serif` generic by that internal name and expects to find `Roboto`.
Since the installed font wasn't named that, Gecko silently fell back to its
own bundled Fira Sans — which rendered very differently and produced the
small-caps appearance. Android's native renderer matches fonts by *file
path* rather than internal name, which is why system UI was unaffected and
the bug looked web-only.

**Fix:** The font's internal `name` table is patched so the family name
resolves as `Roboto`. Two defensive changes ride along with it:

1. **STAT table** — a `wght=400 Regular` named instance is added. The
   original font had no named Regular instance, which can confuse Gecko's
   weight-instance selection.

2. **GSUB small-caps** — no-op `smcp` and `c2sc` OpenType features are added,
   built from inline copies of the regular a–z / A–Z glyph outlines. This is
   a safety net: if any site's CSS genuinely requests small-caps, Gecko uses
   these real glyphs instead of synthesizing them from uppercase letters
   (synthesized small-caps was the visual symptom). Inline copies are used
   rather than composite glyphs because Gecko mis-rendered composite-based
   substitutions at bold weight.

The rename is the actual fix. The STAT and GSUB changes are defensive extras.

---

## Cyrillic / Greek (fixed in v1.2.1)

**Symptom:** Russian and Ukrainian text showed boxes (tofu) mixed into the
text.

**Root cause:** Google Sans Flex contains no Cyrillic or Greek glyphs at all
— not in any build Google distributes (verified against the official Google
Fonts release and Pixel system dumps; Pixels themselves quietly fall back to
Roboto for these scripts). Stock Android has no separate Cyrillic/Greek
fallback font because Roboto itself is that coverage — so once this module
masks every Roboto file with a Latin-only font, those characters have
nowhere to fall back to.

**Fix:** The module bundles **Google Sans** (the non-Flex sibling, which has
full Cyrillic — including Ukrainian І ї Є ґ — and Greek) as
`GoogleSansVF.ttf`, registered as the first fallback family in the system
font configuration. It's the same superfamily, so mixed-script text keeps a
consistent Google Sans look.

One subtlety matters here: since Android 13 the renderer reads
`/system/etc/font_fallback.xml`, not the legacy `fonts.xml` (which is kept
only for apps that parse it directly). The module therefore patches and
installs **both** files — a fallback family added only to `fonts.xml` is
silently ignored on modern Android.

v1.2.x also upgrades the main font to the official Google Fonts v4.005
build, which adds a `slnt` (slant) axis. The config entries for italic now
instantiate it (stock declares an `ital` axis Google Sans Flex doesn't
have), so system italics are real obliques instead of being silently
ignored. Bold/italic entries for the masked NotoSerif files get explicit
`wght`/`slnt` values for the same reason.

---

## Installing

1. Download the zip from the [Releases](../../releases) page.
2. Flash it in Magisk Manager.
3. Reboot.

No prompts. The module installs the full 20-weight Roboto-named set (required
by Gecko) plus GoogleSans / DroidSans / ProductSans / NotoSerif compatibility
symlinks for broader app and ROM support. All installed font files are
symlinks back to a single patched `Font.ttf`, plus the real
`GoogleSansVF.ttf` for Cyrillic/Greek fallback.

---

## Rebuilding the font

Both fonts come from Google Fonts (find the current variable-TTF URLs via
`https://fonts.google.com/download/list?family=Google%20Sans%20Flex` and
`...family=Google%20Sans`). `files/GoogleSansVF.ttf` is the Google Sans
variable TTF, unmodified. `files/Font.ttf` is the Google Sans Flex variable
TTF run through `patch_font.py`, which requires
[fonttools](https://github.com/fonttools/fonttools):

```bash
pip install fonttools
python3 patch_font.py GoogleSansFlex.ttf files/Font.ttf
```

`files/fonts.xml` and `files/font_fallback.xml` are the stock LineageOS /
AOSP font configs with three kinds of edits: the Google Sans fallback family
inserted first in the fallback list, `ital` axis references replaced with
the font's real `slnt` axis, and explicit `wght`/`slnt` values on entries
whose stock file the module masks. If your ROM's stock configs differ
significantly, re-apply those edits to your device's own copies.

The script applies three patches in sequence and runs a self-check on exit.
You can also verify an already-built font manually:

```bash
python3 - <<'EOF'
from fontTools.ttLib import TTFont
f = TTFont("files/Font.ttf")
print("family name :", f["name"].getDebugName(1))
feats = sorted({x.FeatureTag for x in f["GSUB"].table.FeatureList.FeatureRecord})
print("GSUB features:", feats)
has_reg = any(
    getattr(av, "Format", None) == 1 and av.AxisIndex == 0 and av.Value == 400
    for av in f["STAT"].table.AxisValueArray.AxisValue
)
print("STAT wght=400:", has_reg)
EOF
# expect: family name "Roboto", smcp/c2sc in features, STAT wght=400 True
```

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

- **Fonts** (`Font.ttf`, `GoogleSansVF.ttf`) — SIL Open Font License 1.1
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

## Disclaimer

This project is unofficial, unaffiliated with and unendorsed by Google. All
trademarks, font assets, and original code referenced here remain the
property of their respective owners. This module is provided **as-is**, with
no warranty of any kind, express or implied, including but not limited to
fitness for a particular purpose or non-infringement. Use it at your own
risk — flashing modules that patch system fonts can affect device stability,
and the author of this fork assumes no liability for damage, data loss, or
other consequences arising from its use. If you are the rights holder of any
asset included here and object to its distribution, please open an issue
and it will be addressed.
