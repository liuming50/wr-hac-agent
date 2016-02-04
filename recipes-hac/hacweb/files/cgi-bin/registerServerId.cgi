#!/usr/bin/perl
#
# Script called through the board side CGI interface to set a
# registration based on the device ID from the server. 
# Arguments:
# ?server=<server IP>&dev_name=<device ID>&ta_proxy=<host>:<port>
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

syslog( "info", "%s", "Method: " . $ENV{'REQUEST_METHOD'} );

syslog( "info", "%s", "Query: " . $ENV{'QUERY_STRING'} );

# Output CGI header
print header('application/json');

my $defaultServer = getDefaultHacServer();

my $hacServer = $defaultServer;

unless ( $ENV{'REQUEST_METHOD'} =~ m|^POST$|i )
{
    exit_func( { msg => "Invalid Request: " . $ENV{'REQUEST_METHOD'},
		 error => 1 } );
}

# Split information into name/value pairs
my @pairs = split(/&/, $ENV{'QUERY_STRING'} );
my %FORM;

foreach my $pair (@pairs)
{
    my ($name, $value) = split(/=/, $pair);
    $value =~ tr/+/ /;
    $value =~ s/%(..)/pack("C", hex($1))/eg;
    $FORM{$name} = $value;

    syslog( "info", "%s", "Parse: [ $pair ] => [ $name ] [ $value ]" );
}

#
# See if there is a Device Manager file already. If there is
# we assme that the device has regisered and the file contains 
# the registration info.
#
my $rawDeviceMgrData;

unless ( 0 == getDefaultSdkCfgData( \$rawDeviceMgrData ) )
{
    syslog( "info", "%s", "Unable to read default device manager configuration!" );
}
else
{
    syslog( "info", "%s", "Device raw mgr data: $rawDeviceMgrData" );
}

my %cfgData;

parseDevMgrData( $rawDeviceMgrData, \%cfgData ); 

if ( exists $FORM{ server } )
{
    $hacServer = $FORM{ server };
}
elsif ( exists $cfgData{ server } )
{
    $hacServer = $cfgData{ server };
}

unless ( $hacServer )
{
    my $msg = "Error: HAC server not specified";
    syslog( "info", "%s", $msg );
    
    print encode_json( { status => "error", message => $msg } );

    exit_func();
}

my $devName;
unless ( exists $FORM{ dev_name } )
{
    my $msg = "Error: Device name not specified";
    syslog( "info", "%s", $msg );
    
    print encode_json( { status => "error", message => $msg } );

    exit_func();
}

$devName = $FORM{ dev_name };

my $httpsProxy;
if ( 0 == getDefaultHttpsProxy( \$httpsProxy ) &&
     !( $httpsProxy =~ m|^\s*$| ) )
{
    useHttpsProxy( $httpsProxy );
    syslog( "info", "%s", "Using HTTPS_PROXY=$httpsProxy" );
}

my $devMgrProxy = "";
if ( ( exists $FORM{ ta_proxy } ) &&
     !( $FORM{ ta_proxy } =~ m|^\s*$| ) )
{
    $devMgrProxy = ";Proxy=" . $FORM{ ta_proxy };
}

#
# Query the server to get the Device Status
#

my $r;
my $errMsg;

my $tokenCSRF = hacGetCSRFToken( $hacServer, \$r, \$errMsg );
if ( $r )
{
    syslog( "info", "%s", "CSRF Token request failed!" );
    print encode_json( { status => "error", message => "CSRF Token request failed!" } );
    exit_func();
}

syslog( "info", "%s", "CSRF Token: $tokenCSRF" );

my $devStatus = hacGetDeviceStatus( $hacServer, $devName, $tokenCSRF,
				    \$r, \$errMsg );

if ( $r )
{
    chomp( $errMsg );

    syslog( "info", "%s", "Error getting status: $errMsg" );
    
    print encode_json( { status => "error", message => $errMsg } );
}
else
{
    my $rslt;
    unless ( $devStatus eq "device not registered" )
    {
	$rslt = encode_json( { status => "ok", registered => $devStatus, 
			       deviceId => $devName, server => $hacServer } );

	my $devCfgData = "WSS:" . $hacServer . ":443;" .
	    "GetUrl=/devmgr/v1//" . $devName . ";" .
	    "ID=" . $devName . $devMgrProxy;

	setDefaultSdkCfgData( $devCfgData . "\n" );
			      
	my $cmd = "systemctl restart hac.service";
	execCmd( $cmd, \$r );
    }
    else
    {
	$rslt = encode_json( { status => "ok", registered => $devStatus } );
    }
    
    syslog( "info", "%s", $rslt );
    print $rslt;
}

exit_func();
