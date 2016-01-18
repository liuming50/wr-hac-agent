#!/usr/bin/perl
#
# Script called through the board side CGI interface to create device
# registration code on a Helix App Cloud Server.  It expects a GET
# method with an optional argument string as follows:
#
# ?dev_name=<device_name>&ta_proxy=hostname:port
#
# The argument is expected to be correct and there is minimal error checking.  
# 

use strict;
use CGI qw/:standard/;

use Sys::Syslog qw(:standard :macros);

use HelixUtils;
use JSON::PP;

# Turn off Helix script logging
setLogOptions( { useSyslog => 1, lvl => 2 } );

# The name of the server to check status
my $hacServer;

# Use HTML output instead of JSON
my $htmlOut = 0;

# Routine to close the syslog facility and exit
sub exit_func
{
    my $data = shift;

    if ( exists ${ $data }{ msg } )
    {
	${ $data }{ msg } =~ s|\r?\n|;|msg;
	syslog( "info", "%s", ${ $data }{ msg } );
    }

    if ( exists ${ $data }{ error } )
    {
	my $msg = "Unknown error";
	$msg = ${ $data }{ msg } if exists ${ $data }{ msg };
	
	if ( $htmlOut )
	{
	    print "Error: $msg\n";
	}
	else
	{
	    print encode_json( { status => "error", message => $msg } );
	}
    }

    closelog();
    exit 0;
}

openlog( "generate_reg.cgi", "", LOG_USER );

# Output CGI header
if ( $htmlOut )
{
    print header('text/html');
}
else
{
    print header('application/json');    
}

# Load default data that we need to register... 
#   HAC server, SDK name & version

syslog( "info", "%s", "Method: " . $ENV{'REQUEST_METHOD'} );

syslog( "info", "%s", "Query: " . $ENV{'QUERY_STRING'} );

my $defaultServer = getDefaultHacServer();

exit_func( { msg => "Error: No default server name!", error => 1 } )
    unless ( $defaultServer );

$hacServer = $defaultServer;

my $sdkVer = getDefaultSdkVer();

exit_func( { msg => "Error: SDK Version unknown!", error => 1 } )
    unless ( $sdkVer );

my ( $sdkName, $boardName ) = getDefaultSdkName();

exit_func( { msg => "Error: SDK Name unknown!", error => 1 } )
    unless ( $sdkName );

# Read in text
my $buffer = $ENV{'QUERY_STRING'};
if ( $ENV{'REQUEST_METHOD'} =~ m|^GET$|i )
{
    syslog( "info", "%s", "GET request: $buffer" );
}
else
{
    exit_func( { msg => "Invalid Request: " . $ENV{'REQUEST_METHOD'},
		 error => 1 } );
}

# Split information into name/value pairs
my @pairs = split(/&/, $buffer);
my %FORM;

foreach my $pair (@pairs)
{
    my ($name, $value) = split(/=/, $pair);
    $value =~ tr/+/ /;
    $value =~ s/%(..)/pack("C", hex($1))/eg;
    $FORM{$name} = $value;

    syslog( "info", "%s", "Parse: [ $pair ] => [ $name ] [ $value ]" );
}

# Use the default board name if it isn't specified
if ( !(exists $FORM{dev_name}) )
{
    my $data = execCmd( "/sbin/ifconfig eth0" );
    
    my $ha = $data;
    $ha =~ s|.*HWaddr (([A-Fa-f0-9]{2}:?){6}).*|$1|sm;
    $ha =~ s|:||g;
    $boardName = $ha;
    $FORM{dev_name} = $ha;
}
else
{
    $boardName = $FORM{dev_name};
}

# If the user specified use_html, we use the value they pass to us
if ( exists $FORM{use_html} )
{
    $htmlOut = $FORM{use_html};
}

my $taProxy;
undef $taProxy;

# If the user didn't specify a value then we don't define $taProxy
unless ($FORM{ta_proxy} =~ m|^\s*$|)
{
    $taProxy = $FORM{ta_proxy};
}

# Check the device name parameter isn't empty
exit_func( { msg => "Invalid device name!", error => 1 } )
    if ( !(exists $FORM{dev_name}) || $FORM{dev_name} =~ m|^\s*$| );

my $httpsProxy;
if ( 0 == getDefaultHttpsProxy( \$httpsProxy ) &&
     !( $httpsProxy =~ m|^\s*$| ) )
{
    useHttpsProxy( $httpsProxy );
    syslog( "info", "%s", "Using HTTPS_PROXY=$httpsProxy" );
}

my $r;
my $errMsg;

my $tokenCSRF = hacGetCSRFToken( $hacServer, \$r, \$errMsg );

exit_func( { msg => $errMsg, error => 1 } ) if ( $r );

syslog( "info", "%s", "CSRF Token: $tokenCSRF" );

my ( $devRegKey, $devUid, $devServerUrl ) =
    hacGenerateNamedTarget( $hacServer, $FORM{dev_name}, $sdkName, $sdkVer,
			    $tokenCSRF, \$r, \$errMsg );

syslog( "info", "%s", "Dev Reg Key, Dev UID, Server URL: " .
	"$devRegKey, $devUid, $devServerUrl" );

exit_func( { msg => $errMsg, error => 1 } ) if ( $r );

my ( $devRegStatus, $devRegExpireTime_s ) = 
	hacGetKeyExpiration( $hacServer, $devRegKey, $tokenCSRF,
			     \$r, \$errMsg );

exit_func( { msg => $errMsg, error => 1 } ) if ( $r );

# Write out the configuration data

my $devCfgData = $devServerUrl . ";ID=" . $devUid;

$devCfgData =  $devCfgData . ";Proxy=" . $taProxy
    if ( defined $taProxy );

syslog( "info", "%s", "Device UID[ $devUid ]\n" );
syslog( "info", "%s", "Device Server Url[ $devServerUrl ]\n" );
syslog( "info", "%s", "Device Mgr Cfg[ $devCfgData ]\n" );

# Write out the configuration data
( 0 == setDefaultSdkCfgData( $devCfgData ) ) or
    exit_func( { msg => "ERROR: Can't write SDK configuration!" ,
                 error => 1 } );

# Restart the HAC service to pick up the new configuration
my $cmd = "systemctl restart hac.service";

# Comment out the next two lines if simulating
execCmd( $cmd, \$r );

syslog( "error", "%s", "ERROR: Restarting HAC service failed!" ) if ( $r );

my $rslt;

if ( $htmlOut )
{
    $rslt = sprintf( "Your Device ID: $boardName Registration code: $devRegKey\n" );
}
else
{
    $rslt = encode_json( { status => "ok", reg_code => $devRegKey, 
			   expires_mins => ( $devRegExpireTime_s  / 60 ) } );       
}

# Send back the result 
print $rslt;

exit_func( { msg => $rslt } );
