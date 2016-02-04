#!/usr/bin/perl
#
# Script called through the board side CGI interface to retreive the
# registration state of the board.
#
# Most of the work is done by parsing the file /etc/default/device_mgr.cfg
# with some checking with the server to validate that information.
# 

use strict;
use CGI qw/:standard/;

use File::Copy;
use Sys::Syslog qw(:standard :macros);

use HelixUtils;
use JSON::PP;

# Turn off Helix script logging
setLogOptions( { useSyslog => 1, lvl => 1 } );

openlog( "devicestatus.cgi", "", LOG_USER );

# Routine to close the syslog facility and exit
sub exit_func
{
    closelog();
    exit 0;
}

# Output CGI header
print header('application/json');

#
# See if there is a Device Manager file already. If there is
# we assme that the device has regisered and the file contains 
# the registration info. (There is probably a more elegant way
# to do this; but, "ls" works.)
#
my $data;

unless ( 0 == getDefaultSdkCfgData( \$data ) )
{
    my $msg = "Device not configured";
    syslog( "info", "%s", $msg );
    print encode_json( { status => "error", message => $msg } );

    exit_func();
}

# The content of the device manager file looks like this:
#  WSS:128.224.74.23:443;GetUrl=/ws/8002;ID=GalGen2_Linux_de2e1427-211c-4a95-b933-cf35ff7006f6

syslog( "info", "%s", "Device raw mgr data: $data" );

#
# Split the line around ';' for the three major parts, SERVER,
# URL, and DEVICEID
#
my ($server, $url, $deviceid, $ta_proxy ) = split(';', $data, 4);

#
# If we have a Proxy setting, crack out the actual proxy part
#
if ( "" eq  $ta_proxy) {
    $ta_proxy = "none";
    }
else {
    $ta_proxy =~ s|^Proxy=||;       # Get rid of 'Proxy='
    }


syslog( "info", "%s",
	"Device mgr server, url, device ID, Proxy: $server, $url, $deviceid, $ta_proxy" );

#
# Split the server into SCHEME, IP, and PORT
#
my ($serverScheme, $serverIP, $serverPort) = split(':', $server, 3);

syslog( "info", "%s",
	"Device server scheme, IP, port: $serverScheme, $serverIP, $serverPort" );

#
# Crack the DEVICEID into the user assigned NAME and server assigned
# ID PART.
#
# Note that we split around the right-most '_' character
#
$deviceid =~ s|^ID=||;       # Get rid of 'ID='

# Device name is everything before the right most '_'
my $devName = $deviceid;
$devName =~ s|(.*)_.*$|$1|;

syslog( "info", "%s", "Device name: $devName" );

# Device ID from the server is everything after the right most '_'
my $devID = $deviceid;
$devID =~ s|.*_(.*)$|$1|;

syslog( "info", "%s", "Device ID: $devID" );

my $httpsProxy;
if ( 0 == getDefaultHttpsProxy( \$httpsProxy ) &&
     !( $httpsProxy =~ m|^\s*$| ) )
{
    useHttpsProxy( $httpsProxy );
    syslog( "info", "%s", "Using HTTPS_PROXY=$httpsProxy" );
}

my $defHacServer = getDefaultHacServer();

my $sdkVersion = getDefaultSdkVer();

$sdkVersion = "" unless defined $sdkVersion;

my ($sdkName, $boardName) =  getDefaultSdkName();

my $httpsProxy;
if ( 0 != getDefaultHttpsProxy( \$httpsProxy ) )
    {
    $httpsProxy = "";
    }
    
#
# Query the server to get the Device Status
#

my $r;
my $errMsg;

my $tokenCSRF = hacGetCSRFToken( $serverIP, \$r, \$errMsg );
if ( $r )
{
    syslog( "info", "%s", "CSRF Token request failed!" );
    print encode_json( { status => "error", message => "CSRF Token request failed!" } );
    exit_func();
}

syslog( "info", "%s", "CSRF Token: $tokenCSRF" );

# EM my $devStatus = hacGetDeviceStatus( $serverIP, $devName, $tokenCSRF,
#			    \$r, \$errMsg );

my $devStatus = hacGetDeviceStatus( $serverIP, $deviceid, $tokenCSRF,
                                    \$r, \$errMsg );
if ( $r )
{
    chomp( $errMsg );

    syslog( "info", "%s", "Error getting status: $errMsg" );
    
    print encode_json( { status => "error", message => $errMsg } );
}
else
{
    my $rslt = encode_json( { status => "ok", registered => $devStatus, deviceName => $devName, 
			      deviceId => $devID, server => $serverIP, serverPort => $serverPort,
			      serverUrl => $url, serverScheme => $serverScheme, ta_proxy => $ta_proxy,
			      https_proxy => $httpsProxy, defHacServer => $defHacServer, 
			      sdkVersion => $sdkVersion, sdkName => $sdkName } );

    syslog( "info", "%s", $rslt );
    
    print $rslt;
}

exit_func();
