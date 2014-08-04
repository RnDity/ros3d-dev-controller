#! /bin/sh

if [ ! -a AUTHORS ]; then
    touch AUTHORS;
fi
if [ ! -a NEWS ]; then
    touch NEWS;
fi
if [ ! -a README ]; then
    touch README;
fi

if [ ! -a ChangeLog ]; then
    touch ChangeLog;
fi

aclocal \
    && automake --add-missing \
    && autoconf

./configure prefix=`pwd`
make
make install

