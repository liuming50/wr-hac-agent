DESCRIPTION = "Helix App Cloud Command Line Support"
LICENSE = "MIT"
LIC_FILES_CHKSUM = "file://${COMMON_LICENSE_DIR}/MIT;md5=0835ade698e0bcf8506ecda2f7b4f302 \
                    file://${COREBASE}/meta/COPYING.MIT;md5=3da9cfbcb788c80a0384361b4de20420"


PN = "haccmds"

SRC_URI = "file://registerTarget \
	   file://HelixUtils.pm \
	   file://JSON/PP.pm \
	   "

S = "${WORKDIR}"

FILES_${PN} += "/usr/sbin \
                /usr/local/lib/site_perl \
		/usr/local/lib/site_perl/JSON"

do_install() {
	install -d ${D}/${sbindir}
        install -m 0755 ${WORKDIR}/registerTarget ${D}/${sbindir}
        install -d ${D}/${prefix}/local/lib/site_perl
        install -d ${D}/${prefix}/local/lib/site_perl/JSON
        install -m 0644 ${WORKDIR}/HelixUtils.pm  ${D}/usr/local/lib/site_perl
        install -m 0644 ${WORKDIR}/JSON/PP.pm  ${D}/usr/local/lib/site_perl/JSON

}

