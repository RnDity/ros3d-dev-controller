#! /bin/sh

#aclocal \
#    && automake --add-missing \
#    && autoconf

autoreconf -if

./configure prefix=`pwd` $CONFIGURE_FLAGS 
make
make install

