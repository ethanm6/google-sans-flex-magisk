#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright 2026 ethanm6 — see LICENSE-GPL3.txt
"""
patch_font.py — Patch Google Sans Flex for use as an Android system font
that renders correctly in Firefox/Gecko (Fennec).

One patch is applied: RENAME the internal font family to "Roboto". Gecko
resolves the CSS `sans-serif` family by the font's internal name and looks
for "Roboto". With the original name ("Google Sans Flex") Gecko cannot
match it and falls back to its bundled Fira Sans, which caused the
small-caps / all-caps rendering bug.

The rename is the entire fix. Earlier versions of this script also added a
STAT wght=400 "Regular" instance (official GSF v4.005 already ships one)
and no-op smcp/c2sc small-caps features as a defensive measure; an A/B test
on-device (2026-07, Fennec on Android 16) confirmed a rename-only font
renders identically, so both extras were dropped.

Usage:
    pip install fonttools
    python3 patch_font.py INPUT.ttf OUTPUT.ttf

If run with no arguments it defaults to:
    python3 patch_font.py Font.ttf Font.patched.ttf
"""

import sys

from fontTools.ttLib import TTFont


def rename_to_roboto(font):
    name = font["name"]
    renames = {
        1:  "Roboto",                       # Family
        2:  "Regular",                      # Subfamily
        3:  "1.001;GOOG;Roboto-Regular",    # Unique ID
        4:  "Roboto Regular",               # Full name
        6:  "Roboto-Regular",               # PostScript name
        16: "Roboto",                       # Typographic Family
        17: "Regular",                      # Typographic Subfamily
    }
    changed = []
    for rec in name.names:
        if rec.nameID in renames and rec.platformID in (1, 3):
            old = rec.toUnicode()
            new = renames[rec.nameID]
            if rec.platformID == 3:          # Windows / UTF-16BE
                rec.string = new.encode("utf-16-be")
            else:                            # Mac / mac_roman
                rec.string = new.encode("mac_roman")
            changed.append((rec.nameID, old, new))
    for nid, old, new in changed:
        print(f"  name {nid}: {old!r} -> {new!r}")
    return changed


def main():
    inp = sys.argv[1] if len(sys.argv) > 1 else "Font.ttf"
    out = sys.argv[2] if len(sys.argv) > 2 else "Font.patched.ttf"

    print(f"Loading {inp}")
    font = TTFont(inp)
    n_cmap = len(font.getBestCmap())

    print("Renaming family to Roboto")
    rename_to_roboto(font)

    font.save(out)
    print(f"Saved {out}")

    # ---- self-check ----
    chk = TTFont(out)
    fam = chk["name"].getDebugName(1)
    ps = chk["name"].getDebugName(6)
    n_cmap_out = len(chk.getBestCmap())
    print("\nVerification:")
    print(f"  family name     : {fam}")
    print(f"  PostScript name : {ps}")
    print(f"  cmap entries    : {n_cmap_out} (input had {n_cmap})")
    assert fam == "Roboto", "rename failed"
    assert ps == "Roboto-Regular", "PostScript rename failed"
    assert n_cmap_out == n_cmap, "cmap changed"
    print("  all checks passed")


if __name__ == "__main__":
    main()
