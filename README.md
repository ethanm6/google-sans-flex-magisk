# UnFont — Google Sans Flex for Android (Magisk module)

Systemlessly replaces the Android system font with **Google Sans Flex**,
patched so it renders correctly in Firefox/Gecko-based browsers. Installs
with zero prompts.

- Module ID: `UnFont`
- Version: `v1.1.0-auto`
- Target environment: LineageOS, Android 16 (untested by upstream on A16)

---

## Credit

This module is forked from **[AndroSYNC](https://github.com/AndroSYNC)**'s
font module, built on the **OMF / MMT-Extended** installer template.
All installer scaffolding — `common/functions.sh`, the MMT-Extended
`customize.sh` template, and the multi-weight symlink installer pattern —
originates there. This fork's contribution is the font patch and a
streamlined, no-prompt installer that removes the ROM-selection menu.

The font itself is **Google Sans Flex**, © Google.

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

## Installing

1. Flash `Google_Sans_Flex_v1.1.0-auto.zip` in Magisk Manager.
2. Reboot.

No prompts. The module installs the full 20-weight Roboto-named set (required
by Gecko) plus GoogleSans / DroidSans / ProductSans / NotoSerif compatibility
symlinks for broader app and ROM support. All installed font files are
symlinks back to a single patched `Font.ttf`.

---

## Rebuilding the font

The patch is scripted in `patch_font.py` and requires
[fonttools](https://github.com/fonttools/fonttools):

```bash
pip install fonttools
python3 patch_font.py Font.ttf Font.patched.ttf
```

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

To package the flashable zip (run from the module root):

```bash
zip -r ../Google_Sans_Flex_v1.1.0-auto.zip . -x ".*"
```

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
