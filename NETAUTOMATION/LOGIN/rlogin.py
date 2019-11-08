#! /usr/bin/expect --
##
## $Id: clogin.in 2255 2010-10-06 20:31:24Z heas $
##
## rancid 2.3.6
## Copyright (c) 1997-2009 by Terrapin Communications, Inc.
## All rights reserved.
##
## This code is derived from software contributed to and maintained by
## Terrapin Communications, Inc. by Henry Kilmer, John Heasley, Andrew Partan,
## Pete Whiting, Austin Schutz, and Andrew Fort.
##
## Redistribution and use in source and binary forms, with or without
## modification, are permitted provided that the following conditions
## are met:
## 1. Redistributions of source code must retain the above copyright
##    notice, this list of conditions and the following disclaimer.
## 2. Redistributions in binary form must reproduce the above copyright
##    notice, this list of conditions and the following disclaimer in the
##    documentation and/or other materials provided with the distribution.
## 3. All advertising materials mentioning features or use of this software
##    must display the following acknowledgement:
##        This product includes software developed by Terrapin Communications,
##        Inc. and its contributors for RANCID.
## 4. Neither the name of Terrapin Communications, Inc. nor the names of its
##    contributors may be used to endorse or promote products derived from
##    this software without specific prior written permission.
## 5. It is requested that non-binding fixes and modifications be contributed
##    back to Terrapin Communications, Inc.
##
## THIS SOFTWARE IS PROVIDED BY Terrapin Communications, INC. AND CONTRIBUTORS
## ``AS IS'' AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED
## TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
## PURPOSE ARE DISCLAIMED.  IN NO EVENT SHALL THE COMPANY OR CONTRIBUTORS
## BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
## CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
## SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
## INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
## CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
## ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
## POSSIBILITY OF SUCH DAMAGE.
# 
#  The expect login scripts were based on Erik Sherk's gwtn, by permission.
# 
# clogin - Cisco login
#
# Most options are intuitive for logging into a Cisco router.
# The default is to enable (thus -noenable).  Some folks have
# setup tacacs to have a user login at priv-lvl = 15 (enabled)
# so the -autoenable flag was added for this case (don't go through
# the process of enabling and the prompt will be the "#" prompt.
# The default username password is the same as the vty password.
#

# Usage line
set usage "Usage: $argv0 \[-dSV\] \[-autoenable\] \[-noenable\] \[-c command\] \
\[-Evar=x\] \[-e enable-password\] \[-f cloginrc-file\] \[-p user-password\] \
\[-r passphrase\] \[-s script-file\] \[-t timeout\] \[-u username\] \
\[-v vty-password\] \[-w enable-username\] \[-x command-file\] \
\[-y ssh_cypher_type\] router \[router...\]\n"

# env(CLOGIN) may contain:
#	x == do not set xterm banner or name

# Password file
set password_file $env(HOME)/.cloginrc
# Default is to login to the router
set do_command 0
set do_script 0
# The default is to automatically enable
set avenable 1
# The default is that you login non-enabled (tacacs can have you login already
# enabled)
set avautoenable 0
# The default is to look in the password file to find the passwords.  This
# tracks if we receive them on the command line.
set do_passwd 1
set do_enapasswd 1
# Save config, if prompted
set do_saveconfig 0
# Sometimes routers take awhile to answer (the default is 10 sec)
set timeoutdflt 45
#
set send_human {.4 .4 .7 .3 5}

# Find the user in the ENV, or use the unix userid.
if {[ info exists env(CISCO_USER) ]} {
    set default_user $env(CISCO_USER)
} elseif {[ info exists env(USER) ]} {
    set default_user $env(USER)
} elseif {[ info exists env(LOGNAME) ]} {
    set default_user $env(LOGNAME)
} else {
    # This uses "id" which I think is portable.  At least it has existed
    # (without options) on all machines/OSes I've been on recently -
    # unlike whoami or id -nu.
    if [ catch {exec id} reason ] {
	send_error "\nError: could not exec id: $reason\n"
	exit 1
    }
    regexp {\(([^)]*)} "$reason" junk default_user
}
if {[ info exists env(CLOGINRC) ]} {
    set password_file $env(CLOGINRC)
}

# Process the command line
for {set i 0} {$i < $argc} {incr i} {
    set arg [lindex $argv $i]

    switch  -glob -- $arg {
	# Expect debug mode
	-d* {
	    exp_internal 1
	# Username
	} -u* {
	    if {! [regexp .\[uU\](.+) $arg ignore user]} {
		incr i
		set username [ lindex $argv $i ]
	    }
	# VTY Password
	} -p* {
	    if {! [regexp .\[pP\](.+) $arg ignore userpasswd]} {
		incr i
		set userpasswd [ lindex $argv $i ]
	    }
	    set do_passwd 0
	# ssh passphrase
	} -r* {
	    if {! [  regexp .\[rR\](.+) $arg ignore passphrase]} {
		incr i
		set vapassphrase [ lindex $argv $i ]
	    }
	# VTY Password
	} -v* {
	    if {! [regexp .\[vV\](.+) $arg ignore passwd]} {
		incr i
		set passwd [ lindex $argv $i ]
	    }
	    set do_passwd 0
	# Version string
	} -V* {
	    send_user "rancid 2.3.6\n"
	    exit 0
	# Enable Username
	} -w* {
	    if {! [regexp .\[wW\](.+) $arg ignore enauser]} {
		incr i
		set enausername [ lindex $argv $i ]
	    }
	# Environment variable to pass to -s scripts
	} -E* {
	    if {[regexp .\[E\](.+)=(.+) $arg ignore varname varvalue]} {
		set E$varname $varvalue
	    } else {
		send_user "\nError: invalid format for -E in $arg\n"
		exit 1
	    }
	# Enable Password
	} -e* {
	    if {! [regexp .\[e\](.+) $arg ignore enapasswd]} {
		incr i
		set enapasswd [ lindex $argv $i ]
	    }
	    set do_enapasswd 0
	# Command to run.
	} -c* {
	    if {! [regexp .\[cC\](.+) $arg ignore command]} {
		incr i
		set command [ lindex $argv $i ]
	    }
	    set do_command 1
	# Expect script to run.
	} -s* {
	    if {! [regexp .\[sS\](.+) $arg ignore sfile]} {
		incr i
		set sfile [ lindex $argv $i ]
	    }
	    if { ! [ file readable $sfile ] } {
		send_user "\nError: Can't read $sfile\n"
		exit 1
	    }
	    set do_script 1
	# save config on exit
	} -S* {
	    set do_saveconfig 1
	# 'ssh -c' cypher type
	} -y* {
	    if {! [regexp .\[eE\](.+) $arg ignore cypher]} {
		incr i
		set cypher [ lindex $argv $i ]
	    }
	# alternate cloginrc file
	} -f* {
	    if {! [regexp .\[fF\](.+) $arg ignore password_file]} {
		incr i
		set password_file [ lindex $argv $i ]
	    }
	# Timeout
	} -t* {
	    if {! [regexp .\[tT\](.+) $arg ignore timeout]} {
		incr i
	        set timeoutdflt [ lindex $argv $i ]
	    }
	# Command file
	} -x* {
	    if {! [regexp .\[xX\](.+) $arg ignore cmd_file]} {
		incr i
		set cmd_file [ lindex $argv $i ]
	    }
	    if [ catch {set cmd_fd [open $cmd_file r]} reason ] {
		send_user "\nError: $reason\n"
		exit 1
	    }
	    set cmd_text [read $cmd_fd]
	    close $cmd_fd
	    set command [join [split $cmd_text \n] \;]
	    set do_command 1
	# Do we enable?
	} -noenable {
	    set avenable 0
	# Does tacacs automatically enable us?
	} -autoenable {
	    set avautoenable 1
	    set avenable 0
	} -* {
	    send_user "\nError: Unknown argument! $arg\n"
	    send_user $usage
	    exit 1
	} default {
	    break
	}
    }
}
# Process routers...no routers listed is an error.
if { $i == $argc } {
    send_user "\nError: $usage"
}

# Only be quiet if we are running a script (it can log its output
# on its own)
if { $do_script } {
    log_user 0
} else {
    log_user 1
}

#
# Done configuration/variable setting.  Now run with it...
#

# Sets Xterm title if interactive...if its an xterm and the user cares
proc label { host } {
    global env
    # if CLOGIN has an 'x' in it, don't set the xterm name/banner
    if [info exists env(CLOGIN)] {
	if {[string first "x" $env(CLOGIN)] != -1} { return }
    }
    # take host from ENV(TERM)
    if [info exists env(TERM)] {
	if [ regexp \^(xterm|vs) $env(TERM) ignore ] {
	    send_user "\033]1;[lindex [split $host "."] 0]\a"
	    send_user "\033]2;$host\a"
	}
    }
}

# This is a helper function to make the password file easier to
# maintain.  Using this the password file has the form:
# add password sl*	pete cow
# add password at*	steve
# add password *	hanky-pie
proc add {var args} { global int_$var ; lappend int_$var $args}
proc include {args} {
    global env
    regsub -all "(^{|}$)" $args {} args
    if { [ regexp "^/" $args ignore ] == 0 } {
	set args $env(HOME)/$args
    }
    source_password_file $args
}

proc find {var router} {
    upvar int_$var list
    if { [info exists list] } {
	foreach line $list {
	    if { [string match [lindex $line 0] $router ] } {
		return [lrange $line 1 end]
	    }
	}
    }
    return {}
}

# Loads the password file.  Note that as this file is tcl, and that
# it is sourced, the user better know what to put in there, as it
# could install more than just password info...  I will assume however,
# that a "bad guy" could just as easy put such code in the clogin
# script, so I will leave .cloginrc as just an extention of that script
proc source_password_file { password_file } {
    global env
    if { ! [file exists $password_file] } {
	send_user "\nError: password file ($password_file) does not exist\n"
	exit 1
    }
    file stat $password_file fileinfo
    if { [expr ($fileinfo(mode) & 007)] != 0000 } {
	send_user "\nError: $password_file must not be world readable/writable\n"
	exit 1
    }
    if [ catch {source $password_file} reason ] {
	send_user "\nError: $reason\n"
	exit 1
    }
}

# Log into the router.
# returns: 0 on success, 1 on failure, -1 if rsh was used successfully
proc login { router user userpswd passwd enapasswd cmethod cyphertype identfile } {
    global command spawn_id in_proc do_command do_script platform passphrase
    global prompt prompt_match u_prompt p_prompt e_prompt sshcmd
    set in_proc 1
    set uprompt_seen 0

    # try each of the connection methods in $cmethod until one is successful
    set progs [llength $cmethod]
    foreach prog [lrange $cmethod 0 end] {
	incr progs -1
	if [string match "telnet*" $prog] {
	    regexp {telnet(:([^[:space:]]+))*} $prog methcmd suffix port
	    if {"$port" == ""} {
		set retval [ catch {spawn telnet $router} reason ]
	    } else {
		set retval [ catch {spawn telnet $router $port} reason ]
	    }
	    if { $retval } {
		send_user "\nError: telnet failed: $reason\n"
		return 1
	    }
	} elseif [string match "ssh*" $prog] {
	    # ssh to the router & try to login with or without an identfile.
	    regexp {ssh(:([^[:space:]]+))*} $prog methcmd suffix port
	    set cmd [join [lindex $sshcmd 0] " "]
	    if {"$port" != ""} {
		set cmd "$cmd -p $port"
	    }
	    if {"$identfile" != ""} {
		set cmd "$cmd -i $identfile"
	    }
	    set retval [ catch {eval spawn [split "$cmd -l $user $router" { }]} reason ]
	    if { $retval } {
		send_user "\nError: $sshcmd failed: $reason\n"
		return 1
	    }
	} elseif ![string compare $prog "rsh"] {
	    if { ! $do_command } {
		if { [llength $cmethod] == 1 } {
		    send_user "\nError: rsh is an invalid method for -x and "
		    send_user "interactive logins\n"
		}
		if { $progs == 0 } {
		    return 1
		}
		continue;
	    }

	    set commands [split $command \;]
	    set num_commands [llength $commands]
	    set rshfail 0
	    for {set i 0} {$i < $num_commands && !$rshfail} { incr i} {
		log_user 0
		set retval [ catch {spawn rsh $user@$router [lindex $commands $i] } reason ]
		if { $retval } {
		    send_user "\nError: rsh failed: $reason\n"
		    log_user 1; return 1
		}
		send_user "$router# [lindex $commands $i]\n"

		# rcmd does not get a pager and no prompts, so we just have to
		# look for failures & lines.
		expect {
		  "Connection refused"	{ catch {close}; catch {wait};
					  send_user "\nError: Connection\
						    Refused ($prog): $router\n"
					  set rshfail 1
					}
		  -re "(Connection closed by|Connection to \[^\n\r]+ closed)" {
					  catch {close}; catch {wait};
					  send_user "\nError: Connection\
						    closed ($prog): $router\n"
					  set rshfail 1
					}
		  "Host is unreachable"	{ catch {close}; catch {wait};
					  send_user "\nError: Host Unreachable:\
						    $router\n"
					  set rshfail 1
					}
		  "No address associated with" {
					  catch {close}; catch {wait};
					  send_user "\nError: Unknown host\
						    $router\n"
					  set rshfail 1
					}
		  -re "\b+"		{ exp_continue }
		  -re "\[\n\r]+"	{ send_user -- "$expect_out(buffer)"
					  exp_continue
					}
		  timeout		{ catch {close}; catch {wait};
					  send_user "\nError: TIMEOUT reached\n"
					  set rshfail 1
					}
		  eof			{ catch {close}; catch {wait}; }
		}
		log_user 1
	    }
	    if { $rshfail } {
		if { !$progs } {
		    return 1
		} else {
		    continue
		}
	    }
	    # fake the end of the session for rancid.
	    send_user "$router# exit\n"
	    # return rsh "success"
	    return -1
	} else {
	    send_user "\nError: unknown connection method: $prog\n"
	    return 1
	}
	sleep 0.3

	# This helps cleanup each expect clause.
	expect_after {
	    timeout {
		send_user "\nError: TIMEOUT reached\n"
		catch {close}; catch {wait};
		if { $in_proc} {
		    return 1
		} else {
		    continue
		}
	    } eof {
		send_user "\nError: EOF received\n"
		catch {close}; catch {wait};
		if { $in_proc} {
		    return 1
		} else {
		    continue
		}
	    }
	}

    # Here we get a little tricky.  There are several possibilities:
    # the router can ask for a username and passwd and then
    # talk to the TACACS server to authenticate you, or if the
    # TACACS server is not working, then it will use the enable
    # passwd.  Or, the router might not have TACACS turned on,
    # then it will just send the passwd.
    # if telnet fails with connection refused, try ssh
    expect {
	-re "(Connection refused|Secure connection \[^\n\r]+ refused)" {
	    catch {close}; catch {wait};
	    if !$progs {
		send_user "\nError: Connection Refused ($prog): $router\n"
		return 1
	    }
	}
	-re "(Connection closed by|Connection to \[^\n\r]+ closed)" {
	    catch {close}; catch {wait};
	    if !$progs {
		send_user "\nError: Connection closed ($prog): $router\n"
		return 1
	    }
	}
	eof { send_user "\nError: Couldn't login: $router\n"; wait; return 1 }
	-nocase "unknown host\r" {
	    send_user "\nError: Unknown host $router\n";
	    catch {close}; catch {wait};
	    return 1
	}
	"Host is unreachable" {
	    send_user "\nError: Host Unreachable: $router\n";
	    catch {close}; catch {wait};
	    return 1
	}
	"No address associated with name" {
	    send_user "\nError: Unknown host $router\n";
	    catch {close}; catch {wait};
	    return 1
	}
	-re "(Host key not found |The authenticity of host .* be established).*\(yes\/no\)\?" {
	    send "yes\r"
	    send_user "\nHost $router added to the list of known hosts.\n"
	    exp_continue
	}
	-re "HOST IDENTIFICATION HAS CHANGED.* \(yes\/no\)\?" {
	    send "no\r"
	    send_user "\nError: The host key for $router has changed.  Update the SSH known_hosts file accordingly.\n"
	    catch {close}; catch {wait};
	    return 1
	}
	-re "Offending key for .* \(yes\/no\)\?" {
	    send "no\r"
	    send_user "\nError: host key mismatch for $router.  Update the SSH known_hosts file accordingly.\n"
	    catch {close}; catch {wait};
	    return 1
	}
	-re "(denied|Sorry)"	{
				  send_user "\nError: Check your passwd for $router\n"
				  catch {close}; catch {wait}; return 1
				}
	"Login failed"		{
				  send_user "\nError: Check your passwd for $router\n"
				  catch {close}; catch {wait}; return 1
				}
	-re "% (Bad passwords|Authentication failed)"	{
				  send_user "\nError: Check your passwd for $router\n"
				  catch {close}; catch {wait}; return 1
				}
	"Press any key to continue" {
				  # send_user "Pressing the ANY key\n"
				  send "\r"
				  exp_continue
				}
	-re "Enter Selection: " {
				  # Catalyst 1900s have some lame menu.  Enter
				  # K to reach a command-line.
				  send "K\r"
				  exp_continue
				}
	-re "Last login:"	{
				  exp_continue
				}
	-re "@\[^\r\n]+ $p_prompt"	{
				  # ssh pwd prompt
				  sleep 1
				  send -- "$userpswd\r"
				  exp_continue
				}
	-re "Enter passphrase.*: " {
				  # sleep briefly to allow time for stty -echo
				  sleep .3
				  send -- "$passphrase\r"
				  exp_continue
				}
	-re "$u_prompt"		{
				  send -- "$user\r"
				  set uprompt_seen 1
				  exp_continue
				}
	-re "$p_prompt"		{
				  sleep 1
				  if {$uprompt_seen == 1} {
					send -- "$userpswd\r"
				  } else {
					send -- "$passwd\r"
				  }
				  exp_continue
				}
	-re "$prompt"		{
				  set prompt_match $expect_out(0,string);
				  break;
				}
	"Login invalid"		{
				  send_user "\nError: Invalid login: $router\n";
				  catch {close}; catch {wait}; return 1
				}
     }
    }

    set in_proc 0
    return 0
}

# Enable
proc do_enable { enauser enapasswd } {
    global do_saveconfig in_proc
    global prompt u_prompt e_prompt
    set in_proc 1

    send "enable\r"
    expect {
	-re "$u_prompt"	{ send -- "$enauser\r"; exp_continue}
	-re "$e_prompt"	{ send -- "$enapasswd\r"; exp_continue}
	"#"		{ set prompt "#" }
	"(enable)"	{ set prompt "> \\(enable\\) " }
	-re "(denied|Sorry|Incorrect)"	{
			  # % Access denied - from local auth and poss. others
			  send_user "\nError: Check your Enable passwd\n";
			  return 1
			}
	"% Error in authentication" {
			  send_user "\nError: Check your Enable passwd\n"
			  return 1
			}
	"% Bad passwords" {
			  send_user "\nError: Check your Enable passwd\n"
			  return 1
			}
    }
    # We set the prompt variable (above) so script files don't need
    # to know what it is.
    set in_proc 0
    return 0
}

# Run commands given on the command line.
proc run_commands { prompt command } {
    global do_saveconfig in_proc platform
    set in_proc 1

    # If the prompt is (enable), then we are on a switch and the
    # command is "set length 0"; otherwise its "terminal length 0".
    # skip if its an extreme (since the pager can not be disabled on a
    # per-vty basis).
    if { [ string compare "extreme" "$platform" ] } {
	if [ regexp -- ".*> .*enable" "$prompt" ] {
	    send "set length 0\r"
	    # This is ugly, but reduces code duplication, allowing the
	    # subsequent expects to handle everything as normal.
	    set command "set logging session disable;$command"
	} else {
	    send "no cli session paging enable\r"
	}
	# match cisco config mode prompts too, such as router(config-if)#,
	# but catalyst does not change in this fashion.
	regsub -all {^(.{1,11}).*([#>])$} $prompt {\1([^#>\r\n]+)?[#>](\\([^)\\r\\n]+\\))?} reprompt
	expect {
	    -re "\b+"				{ exp_continue }
	    -re "\[\n\r]+"			{ send_user -- "$expect_out(buffer)"
						  exp_continue
						}
	    -re "^\[^\n\r *]*$reprompt"		{ send_user -- "$expect_out(buffer)"
						}
	    -re "^\[^\n\r]*$reprompt."		{ send_user -- "$expect_out(buffer)"
						  exp_continue
						}
	}
    } else {
	set reprompt $prompt
    }

    # this is the only way i see to get rid of more prompts in o/p..grrrrr
    log_user 0

    set commands [split $command \;]
    set num_commands [llength $commands]
    # the pager can not be turned off on the PIX, so we have to look
    # for the "More" prompt.  the extreme is equally obnoxious, with a
    # global switch in the config.
    for {set i 0} {$i < $num_commands} { incr i} {
	send -- "[subst -nocommands [lindex $commands $i]]\r"
	expect {
	    -re "\b+"				{ exp_continue }
	    -re "\[\n\r]+"			{ send_user -- "$expect_out(buffer)"
						  exp_continue
						}
	    -re "^\[^\n\r *]*$reprompt"		{ send_user -- "$expect_out(buffer)"
						}
	    -re "^\[^\n\r]*$reprompt."		{ send_user -- "$expect_out(buffer)"
						  exp_continue
						}
        -re "^.*END\\)"     {
                          send " \r\n"
                          exp_continue
                        }
        -re "lines.*\[\r\n]*" {
                          send " "
                          exp_continue
                        }
	    -re "^--More--\[\r\n]+"		{ # specific match c1900 pager
						  send " "
						  exp_continue
						}
	    -re "\[^\r\n]*Press <SPACE> to cont\[^\r\n]*"	{
						  send " "
						  # bloody ^[[2K after " "
						  expect {
							-re "^\[^\r\n]*\r" {}
							}
						  exp_continue
						}
	    -re "^ *--More--\[^\n\r]*"		{
						  send " "
						  exp_continue }
	    -re "^<-+ More -+>\[^\n\r]*"	{
						  send_user -- "$expect_out(buffer)"
						  send " "
						  exp_continue }
	}
    }
    log_user 1

    if { [ string compare "extreme" "$platform" ] } {
	send -h "exit\r"
    } else {
	send -h "quit\r"
    }
    expect {
	-re "^\[^\n\r *]*$reprompt"		{
						  # the Cisco CE and Jnx ERX
						  # return to non-enabled mode
						  # on exit in enabled mode.
						  send -h "exit\r"
						  exp_continue;
						}
	"The system has unsaved changes"	{ # Force10 SFTOS
						  if {$do_saveconfig} {
						    catch {send "y\r"}
						  } else {
						    catch {send "n\r"}
						  }
						  exp_continue
						}
	"Would you like to save them now"	{ # Force10
						  if {$do_saveconfig} {
						    catch {send "y\r"}
						  } else {
						    catch {send "n\r"}
						  }
						  exp_continue
						}
	-re "(Profile|Configuration) changes have occurred.*"	{
						  # Cisco CSS
						  if {$do_saveconfig} {
						    catch {send "y\r"}
						  } else {
						    catch {send "n\r"}
						  }
						  exp_continue
						}
	"Do you wish to save your configuration changes" {
						  if {$do_saveconfig} {
						    catch {send "y\r"}
						  } else {
						    catch {send "n\r"}
						  }
						  exp_continue
						}
	-re "\[\n\r]+"				{ exp_continue }
	timeout					{ catch {close}; catch {wait};
						  return 0
						}
	eof					{ return 0 }
    }
    set in_proc 0
}

#
# For each router... (this is main loop)
#
source_password_file $password_file
set in_proc 0
set exitval 0
set prompt_match ""
set enable 0
foreach router [lrange $argv $i end] {
    set router [string tolower $router]
    # attempt at platform switching.
    set platform ""
    send_user -- "$router\n"

    # device timeout
    set timeout [find timeout $router]
    if { [llength $timeout] == 0 } {
	set timeout $timeoutdflt
    }

    # Default prompt.
    set prompt "(>|#| \\(enable\\))"

    # look for noenable option in .cloginrc
    if { [find noenable $router] == "1" } {
	set enable 0
    }

    # Figure out passwords
    if { $do_passwd || $do_enapasswd } {
      set pswd [find password $router]
      if { [llength $pswd] == 0 } {
	send_user -- "\nError: no password for $router in $password_file.\n"
	continue
      }
      if { $enable && $do_enapasswd && $autoenable == 0 && [llength $pswd] < 2 } {
	send_user -- "\nError: no enable password for $router in $password_file.\n"
	continue
      }
      set passwd [join [lindex $pswd 0] ""]
      set enapasswd [join [lindex $pswd 1] ""]
    } else {
	set passwd $userpasswd
	set enapasswd $enapasswd
    }

    # Figure out username
    if {[info exists username]} {
      # command line username
      set ruser $username
    } else {
      set ruser [join [find user $router] ""]
      if { "$ruser" == "" } { set ruser $default_user }
    }

    # Figure out username's password (if different from the vty password)
    if {[info exists userpasswd]} {
      # command line username
      set userpswd $userpasswd
    } else {
      set userpswd [join [find userpassword $router] ""]
      if { "$userpswd" == "" } { set userpswd $passwd }
    }

    # Figure out enable username
    if {[info exists enausername]} {
      # command line enausername
      set enauser $enausername
    } else {
      set enauser [join [find enauser $router] ""]
      if { "$enauser" == "" } { set enauser $ruser }
    }

    # Figure out prompts
    set u_prompt [find userprompt $router]
    if { "$u_prompt" == "" } {
	set u_prompt "(Username|Login|login|user name|User):"
    } else {
	set u_prompt [join [lindex $u_prompt 0] ""]
    }
    set p_prompt [find passprompt $router]
    if { "$p_prompt" == "" } {
	set p_prompt "(\[Pp]assword|passwd|Enter password for \[^ :]+):"
    } else {
	set p_prompt [join [lindex $p_prompt 0] ""]
    }
    set e_prompt [find enableprompt $router]
    if { "$e_prompt" == "" } {
	set e_prompt "\[Pp]assword:"
    } else {
	set e_prompt [join [lindex $e_prompt 0] ""]
    }

    # Figure out identity file to use
    set identfile [join [lindex [find identity $router] 0] ""]

    # Figure out passphrase to use
    if {[info exists avpassphrase]} {
	set passphrase $avpassphrase
    } else {
	set passphrase [join [lindex [find passphrase $router] 0] ""]
    }
    if { ! [string length "$passphrase"]} {
	set passphrase $passwd
    }

    # Figure out cypher type
    if {[info exists cypher]} {
        # command line cypher type
        set cyphertype $cypher
    } else {
        set cyphertype [find cyphertype $router]
        if { "$cyphertype" == "" } { set cyphertype "3des" }
    }

    # Figure out connection method
    set cmethod [find method $router]
    if { "$cmethod" == "" } { set cmethod {{telnet} {ssh}} }

    # Figure out the SSH executable name
    set sshcmd [find sshcmd $router]
    if { "$sshcmd" == "" } { set sshcmd {ssh} }

    # Login to the router
    if {[login $router $ruser $userpswd $passwd $enapasswd $cmethod $cyphertype $identfile]} {
	incr exitval
	# if login failed or rsh was unsuccessful, move on to the next device
	continue
    }
    # Figure out the prompt.
    if { [regexp -- "(#| \\(enable\\))" $prompt_match junk] == 1 } {
	set enable 0
    } else {
	if { $avenable == 0 } {
	    set enable 0
	} else {
	    set ne [find noenable $router]
	    set ae [find autoenable $router]
	    if { "$ne" == "1" || "$ae" == "1" || $avautoenable } {
		set enable 0
	    } else {
		set enable 1
	    }
	}
    }
    if { $enable } {
	if {[do_enable $enauser $enapasswd]} {
	    if { $do_command || $do_script } {
		incr exitval
		catch {close}; catch {wait};
		continue
	    }
	}
    }
    # we are logged in, now figure out the full prompt
    send "\r"
    expect {
	-re "\[\r\n]+"		{ exp_continue; }
	-re "^(.+\[:.])1 ($prompt)" { # stoopid extreme cmd-line numbers and
				  # prompt based on state of config changes,
				  # which may have an * at the beginning.
				  set junk $expect_out(1,string)
				  regsub -all "^\\\* " $expect_out(1,string) {} junk
				  regsub -all "\[\]\[\(\)]" $junk {\\&} junk;
				  set prompt ".? ?$junk\[0-9]+ $expect_out(2,string)";
				  set platform "extreme"
				}
	-re "^.+$prompt"	{ set junk $expect_out(0,string);
				  regsub -all "\[\]\[\(\)]" $junk {\\&} prompt;
				}
    }

    if { $do_command } {
	if {[run_commands $prompt $command]} {
	    incr exitval
	    continue
	}
    } elseif { $do_script } {
	# If the prompt is (enable), then we are on a switch and the
	# command is "set length 0"; otherwise its "terminal length 0".
	if [ regexp -- ".*> .*enable" "$prompt" ] {
	    send "set length 0\r"
	    expect -re $prompt  {}
	    send "set width 80\r"
	    expect -re $prompt	{}
	    send "set logging session disable\r"
	} else {
	    send "terminal length 0\r"
	    expect -re $prompt  {}
	    send "terminal width 80\r"
	}
	expect -re $prompt	{}
	source $sfile
	catch {close};
    } else {
	label $router
	log_user 1
	interact
    }

    # End of for each router
    catch {wait};
    sleep 0.3
}
exit $exitval
