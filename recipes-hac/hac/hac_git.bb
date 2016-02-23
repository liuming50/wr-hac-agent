DESCRIPTION = "Helix App Cloud Target Communication Agent"
HOMEPAGE = "http://wiki.eclipse.org/TCF"
BUGTRACKER = "https://bugs.eclipse.org/bugs/"

LICENSE = "EPL-1.0 | EDL-1.0"
LIC_FILES_CHKSUM = "file://${WORKDIR}/hac.service;md5=b105f411c76cfdad3905b2b2edcdbd40"

SRCREV = "4191bbcef38ee288c918b92a9d40450a4655b5a7"

PV = "wb_vadk+git${SRCPV}"

# The config files are machine specific
PACKAGE_ARCH = "${MACHINE_ARCH}"

# Origin location: git://git.wrs.com/git/projects/tcf-c-core.git
SRC_URI = "git://github.com/WindRiver-OpenSourceLabs/tcf-c-core.git;branch=hac \
	   file://hac.init \
	   file://hac.service \
	   "

DEPENDS = "util-linux openssl"

# RDEPENDS_${PV} = "perl"

S = "${WORKDIR}/git"

LSRCPATH = "${S}/examples/device"

inherit update-rc.d systemd

SYSTEMD_SERVICE_${PN} = "hac.service"

INITSCRIPT_NAME = "hac"
INITSCRIPT_PARAMS = "start 99 3 5 . stop 20 0 1 2 6 ."

# mangling needed for make
MAKE_ARCH = "`echo ${TARGET_ARCH} | sed s,i.86,i686,`"
MAKE_OS = "`echo ${TARGET_OS} | sed s,^linux.*,GNU/Linux,`"

EXTRA_OEMAKE = "MACHINE=${MAKE_ARCH} OPSYS=${MAKE_OS} 'CC=${CC}' 'AR=${AR}' 'Conf=Release'"

do_compile() {
	export CONFIGURE_FLAGS="--host=${MAKE_ARCH}-gnu-linux"
	oe_runmake -C ${LSRCPATH}
}

do_install() {
	install -d ${D}${sbindir}
	oe_runmake -C ${LSRCPATH} install INSTALLDIR=${D}${sbindir}
	install -d ${D}${sysconfdir}
	install -d ${D}${sysconfdir}/init.d/
	install -m 0755 ${WORKDIR}/hac.init ${D}${sysconfdir}/init.d/hac

	# systemd
	install -d ${D}${sysconfdir}/hac/
	install -m 0755 ${WORKDIR}/hac.init ${D}${sysconfdir}/hac
	install -d ${D}${systemd_unitdir}/system
	install -m 0644 ${WORKDIR}/hac.service ${D}${systemd_unitdir}/system

}

