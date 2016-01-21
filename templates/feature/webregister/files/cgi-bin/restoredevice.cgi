#!/usr/bin/perl
#
# Script called through the board side CGI interface to restore the board to it's
# previous registration state
#
# This script just finds the backup of the /etc/default/device_mgr.cfg file
# and restores it.
#
# TODO: Should probably write a restore device script
use strict;
use CGI qw/:standard/;

use File::Copy;
use Sys::Syslog qw(:standard :macros);

use HelixUtils;
use JSON::PP;

openlog( "restoredevce.cgi", "", LOG_USER );

my $devmgrfile = "/etc/default/device_mgr.cfg";
my $devmgrbackupfile = "/etc/default/device_mgr.bak";


# See if there is a Device Manager file already. If there is
# we assme that the device has regisered and the file contains 
# the registration info.

# Output CGI header
print header('text/plain');

if ( -r "$devmgrbackupfile" )
{
    syslog( "info", "%s",
	    "Detected existing device manager backupfile, " . 
	    "renaming to $devmgrfile" );
    if ( move( $devmgrbackupfile, $devmgrfile ) )
    {	
    print encode_json( { status => "ok", message => "Device configuration restored" } );
    }
    else
    {
	syslog( "info", "%s",
		"ERROR: restoring device manager file failed!" );
	print encode_json( { status => "error", 
	                    message => "Device configuration file move failed" } );
	closelog();
	exit 0;
    }
}
else
{
    syslog( "info", "%s",
	    "Device not previously configured" );
    print encode_json( { status => "error", 
                         message => "Device not previously configured" } );
    closelog();
    exit 0;
}

# Restart the HAC service
my $cmd = "systemctl restart hac.service";
my $r;

# Comment the next two lines if simulating
execCmd( $cmd, \$r );

syslog( "error", "%s", "ERROR: Restarting HAC service failed!" ) if ( $r );

closelog();

exit 0;
