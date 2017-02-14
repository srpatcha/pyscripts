#!/usr/bin/python
""" Check to see if a TCP port is open """

import os
import checkport
from cdkutils.unittestbase import UnitTestBase

# adjust these constants as needed
DEBUG_UNITTESTS = False
TOGGLE_VAGRANT = False # takes three minutes for vagrant up and another for vagrant down...
TELNET_CLOSED = False
BOGUS_PORT = 23333

class PortCheckTest(UnitTestBase):
    # pylint: disable=too-many-public-methods
    """ Unit tests for PortCheck class """

    @classmethod
    def setUpClass(cls):
        """ perform vagrant up so we have a VM to test against... """
        cls.init_logger(DEBUG_UNITTESTS)
        if TOGGLE_VAGRANT:
            os.system("vagrant up")

    @classmethod
    def tearDownClass(cls):
        """ perform vagrant halt... """
        if TOGGLE_VAGRANT:
            os.system("vagrant halt")

    def test_check_open_port(self):
        """ unit test open condition """
        checker = checkport.PortCheck(checkport.VM_IP, checkport.SSH_PORT, self.logger)
        self.assertTrue(checker.port_open())

    def test_check_telnet_status(self):
        """ unit test open condition """
        checker = checkport.PortCheck(checkport.VM_IP, checkport.TELNET_PORT, self.logger)
        if TELNET_CLOSED:
            self.assertFalse(checker.port_open())
        else:
            self.assertTrue(checker.port_open())

    def test_check_closed_port(self):
        """ unit test closed condition """
        checker = checkport.PortCheck(checkport.VM_IP, BOGUS_PORT, self.logger)
        self.assertFalse(checker.port_open())
