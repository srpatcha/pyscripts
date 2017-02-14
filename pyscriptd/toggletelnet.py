#!/usr/bin/python
# DIAM-608 story.
""" FYI: since this script edits a configuration file in /etc/xinetd.d and toggles a service,
    it must be run as root!!!! (Enforced by the script itself...) """

# pylint: disable=too-many-branches
import os
import sys
import getopt
import traceback
import logging
from cdkutils.logger import Logger
from cdkutils.xinetsvc import XInetService, RootException, LinuxVersionException, SystemCtlService
from cdkutils.osenv import OSEnvironment

LOGGER = Logger()
SERVICE_NAME = 'telnet'

def execute_system_cmd(cmd):
    """ Execute a system cmd. Send all os.system calls through
        here for logging purposes... """
    LOGGER.debug("Executing '%s'..." % cmd)
    os.system(cmd)

class CrontabEditor(object):
    """ add/remove entries in crontab """

    # just static methods so could be functions, but encapsulate them together...
    @staticmethod
    def add_entry(schedule, command):
        """ add a command to crontab... """
        #pylint: disable=line-too-long
        cmd = '(crontab -l ; echo "%s %s > /dev/null 2>&1") 2>&1 | grep -v "no crontab" | sort | uniq | crontab -' % (schedule, command)
        LOGGER.info("crontab: Run '%s' on schedule '%s'" % (command, schedule))
        execute_system_cmd(cmd)

    @staticmethod
    def delete_entry(command):
        """ delete an entry from crontab... """
        #pylint: disable=line-too-long
        cmd = '(crontab -l) 2>&1 | grep -v "no crontab" | grep -v "%s" | sort | uniq | crontab -' % command
        LOGGER.info("crontab: Delete entry '%s'" % command)
        execute_system_cmd(cmd)

def usage():
    """ display usage and exit """
    print("toggletelnet.py [-d] [-s service] [on/off]")
    print("\t-d turns on debug level logging")
    print("\t-h shows help (this info)")
    print("\tif on or off aren't specified, the service status is inverted")
    print("\t\t(e.g. off -> on or vice versa")
    print("\tservice defaults to telnet")
    sys.exit()

class LinuxService(object):
    """ linux service """
    def __init__(self, service_name='telnet'):
        """ constructor """
        self.service_name = service_name
        env = OSEnvironment()
        #first approx for a centos7 DMS...
        if env.get_version() == 'centos' and env.check_minimum_version("7.0.0"):
            self.service = SystemCtlService(service_name, LOGGER)
        else:
            self.service = XInetService(service_name, LOGGER)

    def set_service_status(self, new_state):
        """ set the service to new_state, adding crontab entry if needed """
        if new_state.lower() == 'on':
            self.service.set_service_status(False)
        elif new_state.lower() == 'off':
            self.service.set_service_status(True)

    def toggle(self):
        """ toggle the service """
        # this could be modified to check for telnet transition -> on,
        # but is never called from within LAC...
        self.service.toggle()

def main():
    """ main function... """
    service_name = SERVICE_NAME
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hs:d", ["help", "service="])
        for opt, arg in opts:
            if opt == '-d':
                LOGGER.set_level(logging.DEBUG)
            elif opt in ('-s', '--service'):
                service_name = arg
            elif opt in ('-h', '--help'):
                usage()
        service = LinuxService(service_name)
        if len(args) > 0:
            service.set_service_status(args[0])
        else:
            service.toggle()
    except IOError:
        err = sys.exc_info()[1]
        LOGGER.error("Error: %s" % err)
        traceback.print_exc(file=sys.stdout)
    except RootException:
        err = sys.exc_info()[1]
        LOGGER.error("RootException: %s" % err)
        traceback.print_exc(file=sys.stdout)
    except LinuxVersionException:
        err = sys.exc_info()[1]
        LOGGER.error("LinuxVersionException: %s" % err)
        traceback.print_exc(file=sys.stdout)

if __name__ == "__main__":
    main()
