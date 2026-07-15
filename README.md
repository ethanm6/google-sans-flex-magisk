# UnFont — Google Sans Flex for Android (Magisk module)

Systemlessly replaces the Android system font with **Google Sans Flex**,
patched so Firefox/Gecko browsers render it correctly. **Google Sans** is
bundled as the Cyrillic/Greek fallback and stock **Roboto** (`RobotoFB.ttf`)
as a last-resort safety net, so nothing that rendered before the module
turns to tofu. Zero-prompt install; updates are offered in Magisk directly.

Built for LineageOS / Android 16. Unofficial — not affiliated with or
endorsed by Google. Provided as-is, without warranty; flash at your own risk.

## Install

1. Download the zip from the [Releases](../../releases) page.
2. Flash it in Magisk.
3. Reboot.

## The Gecko fix

Firefox resolves the CSS `sans-serif` family by the font's *internal* name
and expects `Roboto`. With a font named "Google Sans Flex" it silently falls
back to Fira Sans, which shows up as small-caps body text on many sites. So
`Font.ttf` is internally renamed to `Roboto` — and the bundled real Roboto
is renamed to `RobotoFB`, so Gecko never sees two fonts claiming that name.

## Rebuilding

Fonts come from [Google Fonts](https://fonts.google.com) and
[roboto-classic](https://github.com/googlefonts/roboto-classic); requires
[fonttools](https://github.com/fonttools/fonttools).

```bash
# main font: rename to Roboto (self-checks on exit); keep ALL its variation
# axes — Android 16's lock-screen clock animates GRAD/ROND
python3 patch_font.py GoogleSansFlex.ttf files/Font.ttf

# Cyrillic/Greek fallback: subset to its job, pin the unused GRAD axis
pyftsubset GoogleSans.ttf \
  --unicodes="U+0020-007E,U+00A0-00FF,U+0300-036F,U+0370-03FF,U+1F00-1FFF,U+0400-04FF,U+0500-052F,U+1C80-1C8F,U+2DE0-2DFF,U+A640-A69F,U+2000-206F,U+20A0-20CF,U+2116" \
  --layout-features='*' --name-IDs='*' --notdef-outline --output-file=gs.ttf
fonttools varLib.instancer gs.ttf GRAD=0 -o files/GoogleSansVF.ttf

# safety net: Roboto internally renamed to RobotoFB, unused wdth axis pinned
fonttools varLib.instancer RobotoFB-renamed.ttf wdth=100 -o files/RobotoFB.ttf

# flashable zip
zip -r ../Google_Sans_Flex.zip . \
  -x ".*" -x ".git/*" -x "README.md" -x "patch_font.py" \
  -x "CHANGELOG.md" -x "update.json"
```

`files/fonts.xml` and `files/font_fallback.xml` are the stock LineageOS/AOSP
configs with the two fallback families added and italics mapped to the real
`slnt` axis — if your ROM's configs differ, re-apply those edits to its own
copies.

## Credit & licensing

Forked from [AndroSYNC](https://github.com/AndroSYNC)'s font module, built
on the [MMT-Extended](https://github.com/Zackptg5/MMT-Extended) installer
template. Per-component licensing — see the [`LICENSE`](LICENSE) index:
fonts SIL OFL 1.1, installer scripts GPL-2.0, font configs Apache-2.0,
`patch_font.py` GPL-3.0-or-later.

## Support

If you find this project useful, you can support development:

[![Support me on Ko-fi](https://ko-fi.com/img/githubbutton_sm.svg)](https://ko-fi.com/ethanm6)
