#!/bin/sh

# The purpose of the fs_final*.sh files is to provide a simple method that a
# template can use to directly manipulate the generated rootfs image.
#
# TOPDIR, TARGET_ARCH, TARGET_VENDOR, TARGET_OS, IMAGE_ROOTFS, WORKDIR, and
# IMAGE_PKGTYPE are all defined coming into this script.  The current working
# directory will be set to IMAGE_ROOTFS, which is the location the rootfs is
# being generated in.


# Places the files used by Helix App Cloud files to implement target based 
# device registration on the rootfs.  Several files are expected to be in the 
# top level build direcory when ths script is executed.  They are:
#
# sdkName.txt - Contains teh SDK name. Should match SDK config.json "key"
# sdkVersion.txt - Contains the SDK version. Must match SDK config.json "version"
# hacServer.cfg - Pointer to the HAC server. 
#
# If these files are absent, default files are used that will not work until
# they are correctly populated.

BASEDIR=$(dirname $0)

# Copy the registerTarget script and supporting perl module to the rootfs
cp $BASEDIR/files/registerTarget $IMAGE_ROOTFS/usr/sbin
chmod a+rx $IMAGE_ROOTFS/usr/sbin/registerTarget
mkdir -p $IMAGE_ROOTFS/usr/local/lib/site_perl
cp $BASEDIR/files/HelixUtils.pm $IMAGE_ROOTFS/usr/local/lib/site_perl
chmod a+r $IMAGE_ROOTFS/usr/local/lib/site_perl/HelixUtils.pm

# Place the required /etc/default/sdkName.txt on the rootfs. If
# there is one in the project dir use it, else use a default one.
if [ -e $TOPDIR/../sdkName.txt ]; then
    cp $TOPDIR/../sdkName.txt $IMAGE_ROOTFS/etc/default
else
    cp $BASEDIR/files/sdkName.txt $IMAGE_ROOTFS/etc/default/sdkName.txt
fi
chmod a+r $IMAGE_ROOTFS/etc/default/sdkName.txt

# Place the required /etc/default/sdkVersion.txt on the rootfs. If
# there is one in the project dir use it, else use a default one.
if [ -e $TOPDIR/../sdkVersion.txt ]; then
    cp $TOPDIR/../sdkVersion.txt $IMAGE_ROOTFS/etc/default/sdkVersion.txt
else
    cp $BASEDIR/files/sdkVersion.txt $IMAGE_ROOTFS/etc/default/sdkVersion.txt
fi
chmod a+r $IMAGE_ROOTFS/etc/default/sdkVersion.txt

# Place the required /etc/default/hacServer.cfg on the rootfs
# The default is to set it to app.cloud.windriver.com
if [ -e $TOPDIR/../hacServer.cfg ]; then
    cp $TOPDIR/../hacServer.cfg $IMAGE_ROOTFS/etc/default
else
    echo "app.cloud.windriver.com" > $IMAGE_ROOTFS/etc/default/hacServer.cfg
fi
chmod a+r $IMAGE_ROOTFS/etc/default/hacServer.cfg

# Place the optional /etc/default/hacProxy.cfg on the rootfs. If
# there is one in the project dir use it, else do nothing.
if [ -e $TOPDIR/../hacProxy.cfg ]; then
    cp $TOPDIR/../hacProxy.cfg $IMAGE_ROOTFS/etc/default/hacProxy.txt
    chmod a+r $IMAGE_ROOTFS/etc/default/hacProxy.cfg
fi

