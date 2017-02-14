#!/usr/bin/python
# DIAM-752 task. (sub-task of DIAM-608)
""" unittests for toggle telnet script... """

import os
import shutil
from cdkutils.xinetsvc import XInetService, RootException, LinuxVersionException, XINETD_PATH, SystemCtlService
from cdkutils.osenv import OSEnvironment
from cdkutils.unittestbase import UnitTestBase

DEBUG_UNITTESTS = True

class XInetServiceTest(UnitTestBase):
    # pylint: disable=too-many-public-methods
    """ Unit tests for XInetService class; it can't toggle the services, etc (running on cygwin) """
    service = None
    env = None
    needs_cleanup = False
    is_root = False
    on_centos = False

    @classmethod
    def setUpClass(cls):
        cls.init_logger(DEBUG_UNITTESTS)
        try:
            cls.env = OSEnvironment()
            if cls.env.is_cygwin():
                cls.needs_cleanup = True
                # since these unit tests are running on cygwin, not the DMS,
                # this builds an /etc/xinet.d directory populated with a telnet config file...
                cls.logger.debug("calling makedirs({0})".format(XINETD_PATH))
                os.makedirs(XINETD_PATH)

                # copy the telnet file from unittest_files...
                shutil.copy("unittest_files/telnet", "{0}/".format(XINETD_PATH))
            if cls.env.is_linux() and cls.env.check_minimum_version("7.0.0"):
                cls.on_centos = True
            if not cls.on_centos:
                cls.service = XInetService('telnet', cls.logger, True)
            #cls.service = toggletelnet.XInetService('telnet', cls.logger)
        except LinuxVersionException as err:
            cls.do_cleanup()
            raise err
        except Exception as err:
            cls.do_cleanup()
            raise err

    @classmethod
    def do_cleanup(cls):
        """ clean up -- extracted to separate method to call from two spots... """
        if cls.needs_cleanup:
            if cls.env.is_cygwin():
                cls.logger.debug("do_cleanup(), zapping '{0}'".format(XINETD_PATH))
                # clean up after ourselves; zap the simulated xinetd.d config stuff ...
                os.remove("{0}/telnet".format(XINETD_PATH))
                os.removedirs(XINETD_PATH)
        cls.needs_cleanup = False

    @classmethod
    def tearDownClass(cls):
        cls.do_cleanup()

    def test_service_exists(self):
        """ unit test for service existance """
        if not self.on_centos:
            self.assertTrue(self.service.service_exists())

    def test_service_disabled(self):
        """ unit test for service status """
        if not self.on_centos:
            self.assertFalse(self.service.is_enabled())

    def test_is_not_root(self):
        """ unit test for non root; cygwin reports non-root... """
        if not self.on_centos:
            self.assertFalse(self.service.is_root())

    def test_toggle(self):
        """ unit test toggle method; it should throw a RootException... """
        if not self.on_centos:
            with self.assertRaises(RootException):
                self.service.toggle()

class SystemCtlServiceTest(UnitTestBase):
    # pylint: disable=too-many-public-methods
    """ Unit tests for SystemCtlService class; it can't toggle the services, etc (running on cygwin) """
    service = None
    env = None
    needs_cleanup = False
    on_centos = False
    is_root = False
    was_running = False

    @classmethod
    def setUpClass(cls):
        cls.init_logger(DEBUG_UNITTESTS)
        try:
            cls.env = OSEnvironment()
            cls.service = SystemCtlService('telnet', cls.logger, True)
            if cls.env.is_linux() and cls.env.check_minimum_version("7.0.0"):
                cls.on_centos = True
                #save telnet status -- to return to that state when we're finished
                cls.was_running = cls.service.is_enabled()
                if cls.service.is_root():
                    cls.is_root = True
                    #enable the service...
                    cls.service.set_service_status(False)
        except LinuxVersionException as err:
            cls.do_cleanup()
            raise err
        except Exception as err:
            cls.do_cleanup()
            raise err

    @classmethod
    def do_cleanup(cls):
        """ clean up -- extracted to separate method to call from two spots... """
        if cls.is_root:
            cls.service.set_service_status(not cls.was_running)
        cls.needs_cleanup = False

    @classmethod
    def tearDownClass(cls):
        cls.do_cleanup()

    def test_service_exists(self):
        """ unit test for service existance """
        if self.on_centos:
            self.assertTrue(self.service.service_exists())
        else:
            self.assertFalse(self.service.service_exists())

    def test_service_disabled(self):
        """ unit test for service status """
        if self.on_centos:
            self.assertTrue(self.service.is_enabled())
        else:
            self.assertFalse(self.service.is_enabled())

    def test_is_not_root(self):
        """ unit test for non root; cygwin reports non-root... """
        if self.is_root:
            self.assertTrue(self.service.is_root())
        else:
            self.assertFalse(self.service.is_root())

    def test_toggle(self):
        """ unit test toggle method """
        if self.is_root:
            self.service.toggle()
            # since we enabled telnet in setup, it should now be disabled...
            self.assertFalse(self.service.is_enabled())
        else:
            # it should throw a RootException from cygwin or not root..
            with self.assertRaises(RootException):
                self.service.toggle()
