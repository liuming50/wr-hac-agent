#!/usr/bin/perl
#
# Script called through the board side CGI interface to create a device for a
# user on a Helix App Cloud Server.  It expects a POST method with an argument
# string as follows:
#
# ?user_name=<user_login_name>&password=<user_pasword>&dev_name=<device_name>
#   &ta_proxy=<proxy>
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
my $hacServer = "nsh-helixapp.wrs.com";

# Routine to close the syslog facility and exit
sub exit_func
{
    my $data = shift;

    if ( exists ${ $data }{ msg } )
    {
	syslog( "info", "%s", ${ $data }{ msg } );
    }

    if ( exists ${ $data }{ error } )
    {
	my $msg = "Unknown error";
	$msg = ${ $data }{ msg } if exists ${ $data }{ msg };

	print encode_json( { status => "error", message => $msg } );
    }

    closelog();
    exit 0;
}

openlog( "create_dev.cgi", "", LOG_USER );

# Output CGI header
print header('application/json');

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
if ( $ENV{'REQUEST_METHOD'} =~ m|^POST$|i )
{
    syslog( "info", "%s", "POST request: $buffer" );
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
    my ($name, $value) = split(/=/, $pair, 2);
    $value =~ tr/+/ /;
    $value =~ s/%(..)/pack("C", hex($1))/eg;
    $FORM{$name} = $value;

    syslog( "info", "%s", "Parse: [ $pair ] => [ $name ] [ $value ]" );
}

# Check the parameters

# Use the default board name if it isn't specified
if ( !(exists $FORM{dev_name}) )
{
    $FORM{dev_name} = getDefaultBoardName();
}

exit_func( { msg => "Invalid device name!", error => 1 } )
    if ( !(exists $FORM{dev_name}) || $FORM{dev_name} =~ m|^\s*$| );

exit_func( { msg => "Invalid user name!", error => 1 } )
    if ( !(exists $FORM{user_name}) || $FORM{user_name} =~ m|^\s*$| );

exit_func( { msg => "Invalid password!", error => 1 } )
    if ( !(exists $FORM{password}) || $FORM{password} =~ m|^\s*$| );

my $usrName = $FORM{user_name};
my $password = $FORM{password};
my $devName = $FORM{dev_name};
my $taProxy;
undef $taProxy;

# If the user didn't specify a value then we don't define $taProxy
unless ($FORM{ta_proxy} =~ m|^\s*$|)
{
    $taProxy = $FORM{ta_proxy};
}

syslog( "info", "%s", "Client arguments: $usrName $password $devName" );

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

my $tokenWRS = hacGetWRSToken( $hacServer, $usrName, $password,
			       $tokenCSRF, \$r, \$errMsg );

exit_func( { msg => $errMsg, error => 1 } ) if ( $r );

syslog( "info", "%s", "WRS Token: $tokenWRS" );

# Generate a target with the specified name
my ( $devUid, $devServerUrl ) = 
    hacRegisterTarget( $hacServer, $usrName, $password, $devName, 
		       $sdkName, $sdkVer, $tokenCSRF, $tokenWRS,
		       \$r, \$errMsg );

exit_func( { msg => $errMsg, error => 1 } ) if ( $r );

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

execCmd( $cmd, \$r );

syslog( "error", "%s", "ERROR: Restarting HAC service failed!" ) if ( $r );

my $rslt = encode_json( { status => "ok", deviceName => $devName, 
			  deviceId => $devUid, server => $hacServer, 
			  serverUrl => $devServerUrl,
			  ta_proxy => ( defined $taProxy ) ? $taProxy : "" } );       

# Send back the result 
print $rslt;

exit_func( { msg => $rslt } );
