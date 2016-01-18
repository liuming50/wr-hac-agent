#!/bin/sh

# The purpose of the fs_final*.sh files is to provide a simple method that a
# template can use to directly manipulate the generated rootfs image.
#
# TOPDIR, TARGET_ARCH, TARGET_VENDOR, TARGET_OS, IMAGE_ROOTFS, WORKDIR, and
# IMAGE_PKGTYPE are all defined coming into this script.  The current working
# directory will be set to IMAGE_ROOTFS, which is the location the rootfs is
# being generated in.

# HAC default web page for lighttpd server
BASEDIR=$(dirname $0)

cp $BASEDIR/files/*.html $IMAGE_ROOTFS/www/pages
chmod a+r $IMAGE_ROOTFS/www/pages/*.html

mkdir -p $IMAGE_ROOTFS/www/pages/cgi-bin
chmod a+rx $IMAGE_ROOTFS/www/pages/cgi-bin
cp $BASEDIR/files/*.cgi $IMAGE_ROOTFS/www/pages/cgi-bin
chmod a+rx $IMAGE_ROOTFS/www/pages/cgi-bin/*.cgi

mkdir -p $IMAGE_ROOTFS/www/pages/scripts
chmod a+rx $IMAGE_ROOTFS/www/pages/scripts
cp $BASEDIR/files/*.js $IMAGE_ROOTFS/www/pages/scripts
chmod a+r $IMAGE_ROOTFS/www/pages/scripts/*.js

# If using lighttpd then we need to fix up the config file to enable 
# cgi processing
if [ -e $IMAGE_ROOTFS/etc/lighttpd.conf ]; then
     echo "Saving pre-exiting lighttpd.conf to lighttpd.conf.orig"
     cp $IMAGE_ROOTFS/etc/lighttpd.conf $IMAGE_ROOTFS/etc/lighttpd.conf.orig
     echo "Pathcing etc/lighttpd.conf to enable CGI"
     $BASEDIR/files/fix_lighttpd.sh $IMAGE_ROOTFS/etc/lighttpd.conf.orig $IMAGE_ROOTFS/etc/lighttpd.conf $IMAGE_ROOTFS/tmp
fi

