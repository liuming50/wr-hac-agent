#!/usr/bin/perl
#
# Script called through the board side CGI interface to reset the board to it's
# out-of-box registration state
#
# This script just creates a backup of the /etc/default/device_mgr.cfg file
# and deletes the original.
#
use strict;
use CGI qw/:standard/;

use File::Copy;
use Sys::Syslog qw(:standard :macros);

use HelixUtils;
use JSON::PP;

openlog( "resetdevice.cgi", "", LOG_USER );

my $devmgrfile = "/etc/default/device_mgr.cfg";
my $devmgrbackupfile = "/etc/default/device_mgr.bak";


# See if there is a Device Manager file already. If there is
# we assme that the device has regisered and the file contains 
# the registration info.

# Output CGI header
print header('application/json');

if ( -r "$devmgrfile" )
{
    syslog( "info", "%s",
	    "Detected existing device manager file, " . 
	    "renaming to $devmgrbackupfile" );
    if ( move( $devmgrfile, $devmgrbackupfile ) )
    {
	print encode_json( { status => "ok", message => "Device reset" } );	
    }
    else
    {
	syslog( "info", "%s",
		"ERROR: renaming device manager file failed!" );
	print encode_json( { status => "error", 
                            message => "Could not backup device configuration" });
    }
}
else
{
    syslog( "info", "%s",
	    "Device not configured" );
    print encode_json( { status => "error", message => "Device is not configured" });;
}

# Restart the HAC service to pick up the new configuration
my $cmd = "systemctl stop hac.service";
my $r;

execCmd( $cmd, \$r );

syslog( "error", "%s", "ERROR: Stopping HAC service failed!" ) if ( $r );

closelog();

exit 0;
