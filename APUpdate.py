#!/usr/bin/python

# AP Updater
# Version 0.6
# Clay Michaels
# Dec-2014
#
# Usage: 
# python APUpdate.py [fleet.CCU]
#
# Requires hosts file with vehicle aliases such as 'apple.803'


import paramiko
import atexit
from time import sleep
import sys
from cStringIO import StringIO

# CCU credentials
CCUUSER = '<SNIPPED USER>'
SSHKEY = '''-----BEGIN DSA PRIVATE KEY-----
<SNIPPED KEY>
-----END DSA PRIVATE KEY-----'''

# Possible AP SSH credentials
APUSER    = '<SNIPPED USER>'
APPASS1 = '<SNIPPED PASSWORD>'
APPASS2 = '<SNIPPED PASSWORD>'


# PARSE ARGUMENTS
debug = False
if debug == True:
    print sys.argv
    print len( sys.argv )
    
if len( sys.argv ) == 3:
    targetCCU = sys.argv[ 1 ]
    if sys.argv[ 2 ] == '1':
        APPassword = APPASS1
    else:
        APPassword = APPASS2
else:
    print 'USAGE:'
    print 'python APUpdate.py [target CCU] [pw]'
    print 'Note: [target CCU] must include the fleet prefix, e.g. facebook.198'
    print 'Note: [pw] must be "1" or "2" and represent the two possible passwords.'
    sys.exit(  )


# SSH INTO CCU
ccu = paramiko.SSHClient(  )
ccuKey = paramiko.DSSKey.from_private_key( StringIO( SSHKEY ) )
ccu.set_missing_host_key_policy( paramiko.AutoAddPolicy(  ) )
try:
    ccu.connect( targetCCU, username = CCUUSER, pkey = ccuKey, timeout = 30 )
    channel=ccu.invoke_shell()
    stdin=channel.makefile('wb')
    stdout=channel.makefile('rb')
except paramiko.BadAuthenticationType:
    print "Error: Bad password."
    sys.exit( 0 )
except paramiko.SSHException:
    print "Error: Possible timeout. Try again."
    sys.exit( 0 )
    
response=channel.recv( 1024 )
#channel.send( "uptime\r" )
#sleep( 1 )
#response=channel.recv( 1024 ).splitlines(  )
#print response[ 1 ]
channel.send( "cat /conf/ME.conf\r" )
sleep( 1 )
response=channel.recv( 1024 ).splitlines(  )
print response[ 9 ]


channel.send( "glider_dump ccu\r" )
sleep( 1 )
ccuip=channel.recv( 1024 ).splitlines(  )[ 7 ][ 13: ]

print 'ccuip:'+ccuip
commonip =  ccuip[:ccuip.rfind('.')]
#print 'commonip',commonip
lastoctet = ccuip[ccuip.rfind('.')+1:]
#print 'lastoctet',lastoctet
lastoctetmodified = str(int(lastoctet)+1)
#print 'lastoctetmodified',lastoctetmodified
apip = commonip + '.' +lastoctetmodified
print 'apip:'+apip


cmd = 'ssh <SNIPPED USER>@' + apip + '\r'
channel.send( cmd )
sleep( 3 )
response=channel.recv( 1024 )
channel.send( 'yes\r' )
sleep( 1 )
response=channel.recv( 1024 )
channel.send( APPassword+'\r' )
sleep( 1 )
channel.send( 'sy\r' )
response=channel.recv( 1024 )
sleep( 1 )
channel.send( 'ac\r' )
response=channel.recv( 1024 )
sleep( 1 )
channel.send( 'set applet lan 1 disable\r' )
response=channel.recv( 1024 )
sleep( 2 )
channel.send( 'set cli lan 1 disable\r' )
response=channel.recv( 1024 )
sleep( 2 )
channel.send( 'set snmp lan 1 disable\r' )
response=channel.recv( 1024 )
sleep( 3 )
channel.send( 'show\r' )
sleep( 2 )
response=channel.recv( 1024 ).splitlines(  )
for line in response[ 7:12 ]:
    print line
print '----------'
print 'If the first column looks like:'
print 'disable', 'enable', 'disable', 'enable', 'disable'
print 'the operation was a success.'
print 'If not, try again with the alternate AP password. (python UpdateAP.py [target CCU] -alt)'

stdout.close(  )
stdin.close(  )
ccu.close(  )
