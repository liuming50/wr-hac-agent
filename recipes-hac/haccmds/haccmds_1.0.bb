DESCRIPTION = "Helix App Cloud Command Line Support"
LICENSE = "MIT"
LIC_FILES_CHKSUM = "file://${COREBASE}/LICENSE;md5=4d92cd373abda3937c2bc47fbc49d690 \
                    file://${COREBASE}/meta/COPYING.MIT;md5=3da9cfbcb788c80a0384361b4de20420"


PN = "haccmds"
PR = "r1"

SRC_URI = "file://registerTarget \
	   file://HelixUtils.pm \
	   "

DEPENDS = "perl"

RPROVIDES_${PN} = "${PN}"

S = "${WORKDIR}"

FILES_${PN} += "/usr/sbin \
                /usr/local/lib/site_perl"

do_install() {
	install -d ${D}/${sbindir}
        install -m 0755 ${WORKDIR}/registerTarget ${D}/${sbindir}
        install -d ${D}/${prefix}/local/lib/site_perl
        install -m 0755 ${WORKDIR}/HelixUtils.pm  ${D}/usr/local/lib/site_perl

}

