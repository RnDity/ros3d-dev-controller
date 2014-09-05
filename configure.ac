PACKAGE=ros3d-controller
VERSION="0.1.0"

AC_INIT(PACKAGE, VERSION)
AC_CONFIG_SRCDIR(src)
AM_INIT_AUTOMAKE([foreign])

AC_PROG_CC
AM_PROG_CC_C_O

PKG_CHECK_MODULES(GLIB, glib-2.0 
                  gobject-2.0 
                  gio-2.0 
                  gio-unix-2.0 
                  json-glib-1.0)

AC_OUTPUT(Makefile src/Makefile)
