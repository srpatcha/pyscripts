#!/usr/bin/python
""" Deliver some sanity to OS version... """
import unittest
import logging
from cdkutils.logger import Logger

class UnitTestBase(unittest.TestCase):
    # pylint: disable=too-many-public-methods
    """ some common functionality for unittests """
    logger = Logger('/tmp/pytest.log')

    @classmethod
    def init_logger(cls, debug_unittests=False):
        """ initialize the logger """
        if debug_unittests:
            cls.logger.set_level(logging.DEBUG)
            cls.logger.debug("Debugging unittests...")
