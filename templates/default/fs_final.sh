#!/bin/sh

# The purpose of the fs_final*.sh files is to provide a simple method that a
# template can use to directly manipulate the generated rootfs image.
#
# TOPDIR, TARGET_ARCH, TARGET_VENDOR, TARGET_OS, IMAGE_ROOTFS, WORKDIR, and
# IMAGE_PKGTYPE are all defined coming into this script.  The current working
# directory will be set to IMAGE_ROOTFS, which is the location the rootfs is
# being generated in.


# The default Helix App Cloud device agent expects or optionally uses some
# per build files.  They are:
#
# hacUser.cfg - Non-default userid to use when starting the Helix Agent  (optonal)

BASEDIR=$(dirname $0)

# Place the optional /etc/default/hacUser.cfg  on the rootfs. If
# there is one in the project dir use it, else teh device agent will
# run as root.
if [ -e $TOPDIR/../hacUser.cfg ]; then
    cp $TOPDIR/../hacUser.cfg $IMAGE_ROOTFS/etc/default/hacUser.cfg
    chmod a+r $IMAGE_ROOTFS/etc/default/hacUser.cfg
fi

exit 0

