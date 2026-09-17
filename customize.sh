# Google Sans Flex — customize.sh
#
# Everything this module needs is already laid out under system/ in the
# zip (real font files + symlinks, plus fonts.xml/font_fallback.xml), so
# Magisk's own installer does all the real work: it extracts the zip and
# applies default ownership/permissions (0644 files, 0755 dirs) on its own.
#
# The one thing that needs a non-default value is font_fallback.xml: stock
# Android ships it with the system_font_fallback_file SELinux context, not
# the generic system_file Magisk would apply by default. Set it here so
# fontd can read the file.
set_permissions() {
  set_perm "$MODPATH/system/etc/font_fallback.xml" 0 0 0644 u:object_r:system_font_fallback_file:s0
}
