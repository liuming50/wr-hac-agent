DESCRIPTION = "Helix App Cloud Web UI Support"
LICENSE = "MIT"
LIC_FILES_CHKSUM = "file://${COREBASE}/LICENSE;md5=4d92cd373abda3937c2bc47fbc49d690 \
                    file://${COREBASE}/meta/COPYING.MIT;md5=3da9cfbcb788c80a0384361b4de20420"

PN = "hacweb"

SRC_URI = "file://pages/index.html \
           file://pages/tgtRegHelp.html \
           file://cgi-bin/create_dev.cgi \
           file://cgi-bin/devicestatus.cgi \
           file://cgi-bin/generate_reg.cgi \
           file://cgi-bin/registerproxy.cgi \
           file://cgi-bin/registerServerId.cgi \
           file://cgi-bin/resetdevice.cgi \
           file://cgi-bin/restoredevice.cgi \
           file://images/AssociateDev.png \
           file://images/CreateDev.png \
           file://images/CreatePIN.png \
           file://images/PinTimeout.png \
           file://images/Proxy.png \
           file://images/Status.png \
           file://pages/index.html \
           file://pages/tgtRegHelp.html \
           file://scripts/associateid.js \
           file://scripts/createdevice.js \
           file://scripts/pincode.js \
           file://scripts/register.js \
           "
S = "${WORKDIR}"

FILES_${PN} += "/www \
                /www/pages \
                /www/pages/cgi-bin \
                /www/pages/scripts \
                /www/pages/images"

do_install() {
	install -d ${D}/www/pages
        install -m 0666 ${WORKDIR}/pages/*.html ${D}/www/pages

        install -d ${D}/www/pages/cgi-bin
        install -m 0755 ${WORKDIR}/cgi-bin/* ${D}/www/pages/cgi-bin

        install -d ${D}/www/pages/images
        install -m 0666 ${WORKDIR}/images/* ${D}/www/pages/images

        install -d ${D}/www/pages/scripts
        install -m 0666 ${WORKDIR}/scripts/* ${D}/www/pages/scripts
}

