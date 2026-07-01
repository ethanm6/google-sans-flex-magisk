FONTDIR=$MODPATH/files
SYSFONT=$MODPATH/system/fonts
PRDFONT=$MODPATH/system/product/fonts
PRDETC=$MODPATH/system/product/etc
SYSETC=$MODPATH/system/etc
SYSXML=$SYSETC/fonts.xml
MODPROP=$MODPATH/module.prop

header() {
    cp $FONTDIR/*ttf $SYSFONT;
	ln -sf Font.ttf  "$SYSFONT/Roboto-Black.ttf"
	ln -sf Font.ttf  "$SYSFONT/Roboto-BlackItalic.ttf"
	ln -sf Font.ttf  "$SYSFONT/Roboto-Bold.ttf"
	ln -sf Font.ttf  "$SYSFONT/Roboto-BoldItalic.ttf"
	ln -sf Font.ttf  "$SYSFONT/Roboto-Medium.ttf"
	ln -sf Font.ttf  "$SYSFONT/Roboto-MediumItalic.ttf"
}

headline() {
    cp $FONTDIR/*ttf $SYSFONT;
	ln -sf Font.ttf  "$SYSFONT/Black.ttf"
	ln -sf Font.ttf  "$SYSFONT/BlackItalic.ttf"
	ln -sf Font.ttf  "$SYSFONT/Bold.ttf"
	ln -sf Font.ttf  "$SYSFONT/BoldItalic.ttf"
	ln -sf Font.ttf  "$SYSFONT/Medium.ttf"
	ln -sf Font.ttf  "$SYSFONT/MediumItalic.ttf"
}

body() {
    cp $FONTDIR/*ttf $SYSFONT;
	ln -sf Font.ttf  "$SYSFONT/Roboto-Italic.ttf"
	ln -sf Font.ttf  "$SYSFONT/Roboto-Light.ttf"
	ln -sf Font.ttf  "$SYSFONT/Roboto-LightItalic.ttf"
	ln -sf Font.ttf  "$SYSFONT/Roboto-Regular.ttf"
	ln -sf Font.ttf  "$SYSFONT/Roboto-Thin.ttf"
	ln -sf Font.ttf  "$SYSFONT/Roboto-ThinItalic.ttf"
}

condensed() {
    cp $FONTDIR/*ttf $SYSFONT;
    ln -sf Font.ttf  "$SYSFONT/RobotoCondensed-Bold.ttf"
	ln -sf Font.ttf  "$SYSFONT/RobotoCondensed-BoldItalic.ttf"
	ln -sf Font.ttf  "$SYSFONT/RobotoCondensed-Italic.ttf"
	ln -sf Font.ttf  "$SYSFONT/RobotoCondensed-Light.ttf"
	ln -sf Font.ttf  "$SYSFONT/RobotoCondensed-LightItalic.ttf"
	ln -sf Font.ttf  "$SYSFONT/RobotoCondensed-Medium.ttf"
	ln -sf Font.ttf  "$SYSFONT/RobotoCondensed-MediumItalic.ttf"
	ln -sf Font.ttf  "$SYSFONT/RobotoCondensed-Regular.ttf"
}

full() { headline; header; body; condensed;
    ln -sf Font.ttf  "$PRDFONT/GoogleSans-Regular.ttf"
	ln -sf Font.ttf  "$PRDFONT/GoogleSans-Italic.ttf"
}

mistu() {
    cp $FONTDIR/*ttf $SYSFONT;
    ln -sf Font.ttf  "$SYSFONT/GoogleSans-Regular.ttf"
	ln -sf Font.ttf  "$SYSFONT/GoogleSans-Bold.ttf"
	ln -sf Font.ttf  "$SYSFONT/GoogleSans-BoldItalic.ttf"
	ln -sf Font.ttf  "$SYSFONT/GoogleSans-Italic.ttf"
	ln -sf Font.ttf  "$SYSFONT/GoogleSans-Medium.ttf"
	ln -sf Font.ttf  "$SYSFONT/GoogleSans-MediumItalic.ttf"
	ln -sf Font.ttf  "$SYSFONT/DroidSans.ttf"
	ln -sf Font.ttf  "$SYSFONT/DroidSansFallback.ttf"
	ln -sf Font.ttf  "$SYSFONT/DroidSans-Bold.ttf"
	ln -sf Font.ttf  "$SYSFONT/NotoSerif-Regular.ttf"
	ln -sf Font.ttf  "$SYSFONT/NotoSerif-Bold.ttf"
	ln -sf Font.ttf  "$SYSFONT/NotoSerif-Italic.ttf"
	ln -sf Font.ttf  "$SYSFONT/NotoSerif-BoldItalic.ttf"
	ln -sf Font.ttf  "$SYSFONT/ProductSans-Regular.ttf"
	ln -sf Font.ttf  "$SYSFONT/ProductSans-Italic.ttf"
	ln -sf Font.ttf  "$SYSFONT/ProductSans-Light.ttf"
	ln -sf Font.ttf  "$SYSFONT/ProductSans-LightItalic.ttf"
	ln -sf Font.ttf  "$SYSFONT/ProductSans-Thin.ttf"
	ln -sf Font.ttf  "$SYSFONT/ProductSans-ThinItalic.ttf"
}

cleanup() {
	cp $FONTDIR/fonts.xml $SYSETC
	rm -rf $FONTDIR
	rmdir -p $PRDFONT
	rm -rf $SYSFONT/UbuntuCondensed-Regular.ttf
}

### INSTALLATION ###
ui_print "   "
ui_print "- Google Sans Flex (Roboto-named, smcp-patched)"
ui_print "- Auto config: Full Roboto set + compatibility goodies"
ui_print "   "
ui_print "- Installing..."
ui_print "   "

mkdir -p $SYSFONT $SYSETC $PRDFONT $PRDETC

full;  sed -ie 3's/$/+FULL&/' $MODPROP
mistu; sed -ie 3's/$/+(gds)&/' $MODPROP

### CLEAN UP ###
ui_print "- Installation completed."
ui_print "- Cleaning up temporary files..."
cleanup

  rm -rf $MODPATH/common
  rm -rf /data/fonts
