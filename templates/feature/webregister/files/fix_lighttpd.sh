#!/bin/sh

# Shell script to enable CGI in for lighttpd server configuration file
#
# fix.sh <input conf file> <output conf file> <temp dir>
sed -e 's/#\([ \t]*"mod_cgi"\)/ \1/' <$1 >$3/t1
sed -e 's/( ".php", ".pl", ".fcgi" )/( ".php", ".pl", ".fcgi", ".cgi" )/' <$3/t1 > $3/t2
sed -e 's/^#\(cgi.assign [ \t]*= ( ".pl"  => "\/usr\/bin\/perl",\)/\1/' <$3/t2 >$3/t3
sed -e 's/^#\([ \t]* ".cgi" => "\/usr\/bin\/perl" )\)/\1/' <$3/t3 >$2
# rm $3/t1 $3/t2 $3/t3

