DESCRIPTION = "Helix App Cloud Web UI Support (lightppd file override)"
LICENSE = "MIT"
LIC_FILES_CHKSUM = "file://${COREBASE}/LICENSE;md5=4d92cd373abda3937c2bc47fbc49d690 \
                    file://${COREBASE}/meta/COPYING.MIT;md5=3da9cfbcb788c80a0384361b4de20420"

# Just insert ourselves before the default lightppd search path
# so it picks u our local files.

FILESEXTRAPATHS_prepend := "${THISDIR}/${PN}:"

