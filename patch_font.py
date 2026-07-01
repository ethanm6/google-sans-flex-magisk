#!/usr/bin/env python3
"""
patch_font.py — Patch Google Sans Flex for use as an Android system font
that renders correctly in Firefox/Gecko (Fennec).

Three patches are applied:

  1. RENAME  the internal font family to "Roboto". Gecko resolves the CSS
     `sans-serif` family by the font's internal name and looks for "Roboto".
     With the original name ("Google Sans Flex") Gecko cannot match it and
     falls back to its bundled Fira Sans, which caused the small-caps /
     all-caps rendering bug. This rename is the actual fix.

  2. STAT    add a named `wght = 400 Regular` instance (the original font has
     no named Regular instance, which can confuse Gecko's instance selection).

  3. SMCP    add no-op `smcp` + `c2sc` OpenType features built from inline
     copies of the a-z / A-Z outlines. Defensive only: if a site genuinely
     requests small-caps, Gecko uses these real glyphs instead of synthesizing
     them from uppercase. Inline copies are used rather than composites
     because Gecko mis-rendered composite-based substitutions at bold weight.

Usage:
    pip install fonttools
    python3 patch_font.py INPUT.ttf OUTPUT.ttf

If run with no arguments it defaults to:
    python3 patch_font.py Font.ttf Font.patched.ttf
"""

import copy
import sys

from fontTools.ttLib import TTFont
from fontTools.ttLib.tables._n_a_m_e import NameRecord
from fontTools.ttLib.tables._g_l_y_f import Glyph, GlyphCoordinates
from fontTools.ttLib.tables import otTables
from fontTools.ttLib.tables.ttProgram import Program


# ---------------------------------------------------------------------------
# 1. Rename internal font family to "Roboto"
# ---------------------------------------------------------------------------
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


# ---------------------------------------------------------------------------
# 2. Add a named wght=400 Regular value to the STAT table
# ---------------------------------------------------------------------------
def add_stat_regular(font):
    stat = font["STAT"].table
    name = font["name"]

    # wght must be axis 0; verify so we don't write a wrong AxisIndex.
    axis_tags = [a.AxisTag for a in stat.DesignAxisRecord.Axis]
    if axis_tags.index("wght") != 0:
        raise RuntimeError(f"Expected wght at axis 0, got order {axis_tags}")

    # Skip if a wght=400 value already exists.
    if stat.AxisValueArray:
        for av in stat.AxisValueArray.AxisValue:
            if getattr(av, "Format", None) == 1 and av.AxisIndex == 0 \
                    and av.Value == 400:
                print("  STAT already has wght=400; skipping")
                return

    # Add a "Regular" name record at the next free nameID.
    reg_id = max(r.nameID for r in name.names) + 1
    for plat_id, enc_id, lang_id in [(3, 1, 0x0409), (1, 0, 0)]:
        nr = NameRecord()
        nr.nameID, nr.platformID, nr.platEncID, nr.langID = \
            reg_id, plat_id, enc_id, lang_id
        nr.string = ("Regular".encode("utf-16-be") if plat_id == 3
                     else "Regular".encode("mac_roman"))
        name.names.append(nr)

    av = otTables.AxisValue()
    av.Format = 1
    av.AxisIndex = 0          # wght
    av.Flags = 0x0002         # ELIDABLE (default, omit from style name)
    av.ValueNameID = reg_id
    av.Value = 400.0

    if stat.AxisValueArray is None:
        stat.AxisValueArray = otTables.AxisValueArray()
        stat.AxisValueArray.AxisValue = []
    stat.AxisValueArray.AxisValue.append(av)
    print(f"  STAT: added wght=400 Regular (ELIDABLE, nameID {reg_id})")


# ---------------------------------------------------------------------------
# 3. Add no-op smcp / c2sc features from inline glyph copies
# ---------------------------------------------------------------------------
def _inline_copy(glyf, src_name, new_name):
    """Return a standalone Glyph that duplicates src_name's outlines."""
    src = glyf[src_name]
    src.expand(glyf)
    if src.isComposite() or src.numberOfContours <= 0:
        return None
    g = Glyph()
    g.numberOfContours = src.numberOfContours
    g.coordinates = GlyphCoordinates(list(src.coordinates))
    g.flags = copy.copy(src.flags)
    g.endPtsOfContours = copy.copy(src.endPtsOfContours)
    g.program = Program()     # no TT hinting
    return g


def _single_subst_lookup(mapping):
    lk = otTables.Lookup()
    lk.LookupType = 1
    lk.LookupFlag = 0
    st = otTables.SingleSubst()
    st.Format = 2
    st.mapping = dict(mapping)
    lk.SubTable = [st]
    lk.SubTableIndex = [0]
    return lk


def add_smallcaps(font):
    cmap = font.getBestCmap()
    glyf = font["glyf"]
    hmtx = font["hmtx"]

    smcp_map, c2sc_map = {}, {}   # lowercase->.sc , uppercase->.sc

    for lo, up in zip("abcdefghijklmnopqrstuvwxyz",
                      "ABCDEFGHIJKLMNOPQRSTUVWXYZ"):
        lg, ug = cmap.get(ord(lo)), cmap.get(ord(up))
        if not lg or not ug:
            continue
        # smcp: lowercase 'a' -> a.sc (copy of 'a' so it renders normally)
        g = _inline_copy(glyf, lg, f"{lg}.sc")
        if g is not None:
            glyf[f"{lg}.sc"] = g
            hmtx.metrics[f"{lg}.sc"] = hmtx.metrics[lg]
            smcp_map[lg] = f"{lg}.sc"
        # c2sc: uppercase 'A' -> A.sc (copy of 'A')
        g2 = _inline_copy(glyf, ug, f"{ug}.sc")
        if g2 is not None:
            glyf[f"{ug}.sc"] = g2
            hmtx.metrics[f"{ug}.sc"] = hmtx.metrics[ug]
            c2sc_map[ug] = f"{ug}.sc"

    # Register new glyph names.
    order = list(font.getGlyphOrder())
    for n in list(smcp_map.values()) + list(c2sc_map.values()):
        if n not in order:
            order.append(n)
    font.setGlyphOrder(order)

    gsub = font["GSUB"].table
    smcp_idx = len(gsub.LookupList.Lookup)
    gsub.LookupList.Lookup.append(_single_subst_lookup(smcp_map))
    c2sc_idx = smcp_idx + 1
    gsub.LookupList.Lookup.append(_single_subst_lookup(c2sc_map))

    for tag, lk_idx in (("smcp", smcp_idx), ("c2sc", c2sc_idx)):
        fr = otTables.FeatureRecord()
        fr.FeatureTag = tag
        fr.Feature = otTables.Feature()
        fr.Feature.FeatureParams = None
        fr.Feature.LookupListIndex = [lk_idx]
        feat_idx = len(gsub.FeatureList.FeatureRecord)
        gsub.FeatureList.FeatureRecord.append(fr)
        # Register in every script and language system so it always applies.
        for sr in gsub.ScriptList.ScriptRecord:
            if sr.Script.DefaultLangSys:
                sr.Script.DefaultLangSys.FeatureIndex.append(feat_idx)
            for lsr in (sr.Script.LangSysRecord or []):
                lsr.LangSys.FeatureIndex.append(feat_idx)

    print(f"  GSUB: added smcp ({len(smcp_map)} glyphs) "
          f"and c2sc ({len(c2sc_map)} glyphs)")


# ---------------------------------------------------------------------------
def main():
    inp = sys.argv[1] if len(sys.argv) > 1 else "Font.ttf"
    out = sys.argv[2] if len(sys.argv) > 2 else "Font.patched.ttf"

    print(f"Loading {inp}")
    font = TTFont(inp)

    print("[1/3] Renaming family to Roboto")
    rename_to_roboto(font)

    print("[2/3] Adding wght=400 Regular to STAT")
    add_stat_regular(font)

    print("[3/3] Adding smcp/c2sc features")
    add_smallcaps(font)

    font.save(out)
    print(f"Saved {out}")

    # ---- self-check ----
    chk = TTFont(out)
    fam = chk["name"].getDebugName(1)
    feats = sorted({f.FeatureTag for f in
                    chk["GSUB"].table.FeatureList.FeatureRecord})
    has_reg = any(getattr(av, "Format", None) == 1 and av.AxisIndex == 0
                  and av.Value == 400
                  for av in chk["STAT"].table.AxisValueArray.AxisValue)
    print("\nVerification:")
    print(f"  family name      : {fam}")
    print(f"  smcp / c2sc      : {'smcp' in feats} / {'c2sc' in feats}")
    print(f"  STAT wght=400    : {has_reg}")
    assert fam == "Roboto", "rename failed"
    assert "smcp" in feats and "c2sc" in feats, "smallcaps failed"
    assert has_reg, "STAT Regular failed"
    print("  all checks passed")


if __name__ == "__main__":
    main()
