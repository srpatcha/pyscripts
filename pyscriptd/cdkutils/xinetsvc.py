#!/usr/bin/python
""" A wrapper around the xinetd services ... """
from cdkutils.osenv import OSEnvironment
import re
import os
import shutil

XINETD_PATH = "/etc/xinetd.d"

class RootException(Exception):
    """ Just extend the Exception class """
    pass

class LinuxVersionException(Exception):
    """ Just extend the Exception class """
    pass

class LinuxService(object):
    """ linux service base class """
    def __init__(self, serviceName, logger, running_test=False):
        self._servicename = serviceName
        self._logger = logger
        self._running_test = running_test

    def get_service_name(self):
        """ return the name of the service """
        return self._servicename

    def is_root(self):
        """ check to see if we're running as root """
        retval = False
        euid = os.geteuid()
        if euid == 0:
            retval = True
        self._logger.debug("is_root(): %s {euid: %s}" % (retval, euid))
        return retval

    def set_service_status(self, disabled=True):
        """ set the service to either enabled or disabled """
        pass

    def service_exists(self):
        """ return true iff a service exists... """
        pass

    def is_enabled(self):
        """ return true iff a service is enabled... """
        pass

    def toggle(self):
        """ toggle the service """
        if not self.is_root():
            raise RootException("Only root can toggle services or edit their configuration")
        if self.service_exists():
            self._logger.debug("Service '%s' exists" % self.get_service_name())
            try:
                if self.is_enabled():
                    self._logger.info("Service '%s' was enabled, toggling to off..." %
                                      (self._servicename))
                    self.set_service_status(True)
                else:
                    self._logger.info("Service '%s' was disabled, toggling to on..." %
                                      (self._servicename))
                    self.set_service_status(False)
            except IOError:
                # already caught the exception and reported it -- just continue...
                pass
        else:
            self._logger.warning("Service '%s' not installed..." % (self.get_service_name()))

class SystemCtlService(LinuxService):
    """ Class to enable/disable/toggle a systemctl service... """
    def __init__(self, serviceName, logger, running_test=False):
        """ constructor... """
        super(SystemCtlService, self).__init__(serviceName, logger, running_test)
        env = OSEnvironment()
        logger.debug("env: %s" % env)

        # if running unit tests from cygwin, we don't care about the linux version...
        if not running_test and not env.is_dms():
            raise LinuxVersionException("Script not supported for %s" % env)
        self._exists = False
        self._running = False
        self.check_service_status()

    def check_service_status(self):
        """ execute systemctl status ?????.socket and parse output """
        tempfile = '/tmp/service.txt'
        infile = None
        try:
            regex1 = re.compile(r"\s*Loaded\:\s*(\S+).*\(")
            regex2 = re.compile(r"\s*Active\:\s*(\S+).*\(")
            os.system("systemctl status {0}.socket > {1}".format(self.get_service_name(), tempfile))
            infile = open(tempfile, "r")
            for line in infile:
                matched = regex1.match(line)
                if matched != None:
                    match_found = True
                    if matched.group(1) == 'not-found':
                        self._exists = False
                        self._running = False
                        break
                    elif matched.group(1) == 'loaded':
                        self._exists = True
                matched = regex2.match(line)
                if matched != None:
                    match_found = True
                    if matched.group(1) == 'inactive':
                        self._running = False
                    elif matched.group(1) == 'active':
                        self._running = True
        finally:
            #cleanup after ourselves...
            if infile != None:
                infile.close()
            #os.remove(tempfile)

    def service_exists(self):
        return self._exists

    def is_enabled(self):
        return self._running

    def set_service_status(self, disabled=True):
        if not self.is_root():
            raise RootException("Only root can toggle services or edit their configuration")
        command = "stop"
        if not disabled:
            command = "start"
        os.system("systemctl {0} {1}.socket".format(command, self.get_service_name()))
        # update _running flag -- the configuration isn't re-read after constructor...
        self._running = not disabled

class XInetService(LinuxService):
    """ Class to enable/disable/toggle a xinetd.d service... """

    def __init__(self, serviceName, logger, running_test=False):
        """ constructor... """
        super(XInetService, self).__init__(serviceName, logger, running_test)

        env = OSEnvironment()
        logger.debug("env: %s" % env)

        # if running unit tests from cygwin, we don't care about the linux version...
        if not running_test and not env.is_dms():
            raise LinuxVersionException("Script not supported for %s" % env)
        self.__cfgfilename = "%s/%s" % (XINETD_PATH, serviceName)
        self.__p = re.compile(r"\s*disable\s*\=\s*(\w+)")

    def service_exists(self):
        """ check to see if the service is even installed """
        return bool(os.path.isfile(self.__cfgfilename))

    def backup_config_file(self):
        """ backup the cfg file... """
        # save a backup copy of the service's cfg file...
        savefile = "/tmp/%s.old" % self._servicename

        # zap an existing savefile...
        if os.path.isfile(savefile):
            os.remove(savefile)
        shutil.copy(self.__cfgfilename, savefile)

    def set_disable(self, disabledflag=True):
        """ Set the services disable flag to disabledflag """
        if disabledflag:
            disabledvalue = "yes"
        else:
            disabledvalue = "no"
        tempname = "/tmp/inetsvc.txt"
        infile = None
        outfile = None
        try:
            infile = open(self.__cfgfilename, "r")
            outfile = open(tempname, "w")
            for line in infile:
                matched = self.__p.match(line)
                if matched != None:
                    outfile.write("        disable = %s\n" % disabledvalue)
                else:
                    outfile.write(line)
            if infile != None:
                infile.close()
                infile = None
            if outfile != None:
                outfile.close()
                outfile = None

            self.backup_config_file()

            # copy the working file into place...
            shutil.copy(tempname, self.__cfgfilename)
        finally:
            #cleanup after ourselves...
            if infile != None:
                infile.close()
            if outfile != None:
                outfile.close()
            os.remove(tempname)

    def is_enabled(self):
        """ return True iff the service is enabled... """
        retval = False
        infile = None
        try:
            infile = open(self.__cfgfilename, "r")
            for line in infile:
                matched = self.__p.match(line)
                if matched != None:
                    if matched.group(1).lower() == 'no':
                        retval = True
                        break
        finally:
            if infile != None:
                infile.close()
        return retval

    def restart_inet(self):
        """ Restart the xinetd daemon... """
        self._logger.debug("Restarting xinetd...")
        os.system('/etc/rc.d/init.d/xinetd restart')

    def exec_chkconfig(self, disabled):
        """ execute chkconfig to change the service's state """
        if disabled:
            servicestate = "off"
        else:
            servicestate = "on"
        self._logger.debug("executing chkconfig %s %s" % (self._servicename, servicestate))
        os.system('/sbin/chkconfig %s %s' % (self._servicename, servicestate))

    def get_cfg_filename(self):
        """ return the name of the service's config file... """
        return self.__cfgfilename

    def get_service_name(self):
        """ return the name of the service """
        return self._servicename

    def is_root(self):
        """ check to see if we're running as root """
        retval = False
        euid = os.geteuid()
        if euid == 0:
            retval = True
        self._logger.debug("is_root(): %s {euid: %s}" % (retval, euid))
        return retval

    def set_service_status(self, disabled=True):
        """ set the service to either enabled or disabled """
        if not self.is_root():
            raise RootException("Only root can toggle services or edit their configuration")

        self._logger.info("set_service_status '%s' disabled: %s..." %
                          (self._servicename, disabled))
        self.set_disable(disabled)
        self.restart_inet()
        self.exec_chkconfig(disabled)
