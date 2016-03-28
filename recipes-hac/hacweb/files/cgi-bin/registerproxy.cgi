#!/usr/bin/perl

# Copyright (c) 2015, 2016 Wind River Systems, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

#
# Script called through the board side CGI interface to get or set the
# proxy interfaces for the HTTPS (registration) 
#
# The POST rest method request takes arguments formatted as follows:
# ?proxy=<url>
#
# When the argument to proxy= is empty the script will clear the proxy
# setting from the system configuration
#
# The GET method request returns the proxy setting in the form:
#  {"status"="ok","proxy"="<url>"}
#

use strict;
use CGI qw/:standard/;

use File::Copy;
use Sys::Syslog qw(:standard :macros);

use HelixUtils;
use JSON::PP;

openlog( "registerproxy.cgi", "", LOG_USER );

# Turn off Helix script logging
setLogOptions( { useSyslog => 1, lvl => 1 } );

# Routine to close the syslog facility and exit
sub exit_func
{
    closelog();
    exit 0;
}

syslog( "info", "%s", "Request method: " . $ENV{'REQUEST_METHOD'} );

# Output CGI header
print header('application/json');

my $httpsProxy;

if ( $ENV{'REQUEST_METHOD'} =~ m|^POST$|i )
{
    unless( $ENV{'QUERY_STRING'} =~ m|^&?proxy=| )
    {
	syslog( "info", "%s", "Unknown POST arguments: " . $ENV{'QUERY_STRING'} );
	print encode_json( { status => "error", message => "Unknown arguments" } );
	exit_func();
    }

    $httpsProxy = $ENV{'QUERY_STRING'};
    $httpsProxy =~ s|^&?proxy=|$1|;
    chomp( $httpsProxy );

    # If there is no argument value we pass undefined
    undef $httpsProxy if ( $httpsProxy =~ m|^\s*$| );

    if ( 0 == setDefaultHttpsProxy( $httpsProxy ) )
    {
	syslog( "info", "%s", "Set HTTPS_PROXY=$httpsProxy" );
	print encode_json( { status => "ok" } );
    }
    else
    {
	syslog( "info", "%s", "Error: Unable to set proxy" );
	print encode_json( { status => "error", message => "Unable to set proxy" } );
    }
}
elsif ( $ENV{'REQUEST_METHOD'} =~ m|^GET$|i )
{
    if ( 0 == getDefaultHttpsProxy( \$httpsProxy ) )
    {
	print encode_json( { status => "ok", proxy => $httpsProxy } );
	syslog( "info", "%s", "Set proxy=$httpsProxy" );
    }
    else
    {
	print encode_json( { status => "ok", proxy => "", 
		message => "Unable to read proxy setting" } );
	syslog( "info", "%s", "Unable to read proxy setting" );
    }
}
else
{
    my $err = "Unknown REQUEST_METHOD " . $ENV{'REQUEST_METHOD'};
    print encode_json( { status => "error", message => $err } );
}

exit_func();
